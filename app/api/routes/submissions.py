from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.submission import Submission
from app.schemas.submission import SubmissionCreate
from app.models.tag import Tag
from app.models.submission_tag import SubmissionTag
from app.oauth2 import get_current_user
from app.models.user import User
from app.models.review import Review
from sqlalchemy import func
from app.schemas.submission import SubmissionUpdate, SubmissionResponse
from app.utils.validators import sanitize_text, validate_code_content
from app.api.routes.helpers import serialize_submission
from fastapi import Query
from sqlalchemy.orm import joinedload
from app.core.logger import logger
from app.config import settings
import cloudinary
import cloudinary.uploader
from fastapi import Form, UploadFile, File
from pydantic import ValidationError
from typing import Optional
import json

router = APIRouter(
    prefix="/api/submissions",
    tags=["Submissions"]
)

# Configure Cloudinary
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True
)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_submission(
    title: str = Form(...),
    description: str = Form(...),
    code_content: str = Form(...),
    language: str = Form(...),
    tags: str = Form("[]"),
    video: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new submission with optional video upload.
    
    Note: This endpoint accepts multipart/form-data.
    When using Postman/API clients, do NOT manually set Content-Type header.
    """
    
    # Check role
    if current_user.role != "student":
        logger.warning(f"User {current_user.id} is not a student")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can create submissions."
        )
    
    # Parse and validate using Pydantic
    try:
        tag_list = json.loads(tags)
        
        # Create Pydantic model for validation
        payload = SubmissionCreate(
            title=title,
            description=description,
            code_content=code_content,
            language=language,
            tags=tag_list
        )
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid tags format. Must be JSON array."
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.errors()
        )
    
    # Sanitize inputs
    title_clean = sanitize_text(payload.title, max_length=200)
    description_clean = sanitize_text(payload.description, max_length=2000)
    code_content_clean = validate_code_content(payload.code_content)
    
    # Create submission
    submission = Submission(
        user_id=current_user.id,
        title=title_clean,
        description=description_clean,
        code_content=code_content_clean,
        language=payload.language
    )
    
    db.add(submission)
    db.commit()
    db.refresh(submission)
    
    logger.info(f"Submission created: id={submission.id}")
    
    # Handle tags
    tag_names = []
    for tag_name in payload.tags:
        tag = db.query(Tag).filter(Tag.name == tag_name).first()
        if not tag:
            tag = Tag(name=tag_name)
            db.add(tag)
            db.commit()
            db.refresh(tag)
        
        link = SubmissionTag(submission_id=submission.id, tag_id=tag.id)
        db.add(link)
        tag_names.append(tag.name)
    
    db.commit()
    
    # Handle video upload
    video_url = None
    if video:
        try:
            # Verify that video file has actual content
            contents = await video.read()
            if len(contents) == 0:
                logger.warning(f"Empty video file received for submission {submission.id}")
            else:
                # Reset file pointer after reading
                await video.seek(0)
                
                video_url = await _upload_video_to_cloudinary(
                    video=video,
                    submission_id=submission.id,
                    user_id=current_user.id
                )
                submission.walkthrough_video_url = video_url
                db.commit()
                db.refresh(submission)
                logger.info(f"Video uploaded for submission {submission.id}")
        except Exception as e:
            logger.error(f"Video upload failed for submission {submission.id}: {str(e)}")
            # Don't fail the whole request if video upload fails
    
    return {
        "id": submission.id,
        "user_id": submission.user_id,
        "title": submission.title,
        "description": submission.description,
        "code_content": submission.code_content,
        "language": submission.language,
        "status": submission.status,
        "tags": tag_names,
        "walkthrough_video_url": video_url,
        "created_at": submission.created_at,
    }


async def _upload_video_to_cloudinary(
    video: UploadFile,
    submission_id: int,
    user_id: int
) -> str:
    """
    Upload video to Cloudinary and return secure URL.
    Raises exception if upload fails.
    """
    
    # Validate file type
    allowed_types = ["video/webm", "video/mp4", "video/quicktime", "video/x-matroska"]
    if video.content_type not in allowed_types:
        raise ValueError(
            f"Invalid file type '{video.content_type}'. "
            f"Allowed: webm, mp4, mov, mkv"
        )
    
    # Validate file size (max 100MB)
    video.file.seek(0, 2)
    file_size = video.file.tell()
    video.file.seek(0)
    
    max_size = 100 * 1024 * 1024  # 100MB
    if file_size > max_size:
        raise ValueError(
            f"File too large ({file_size / 1024 / 1024:.1f}MB). "
            f"Maximum size is 100MB"
        )
    
    logger.info(
        f"Uploading video for submission {submission_id} "
        f"(size: {file_size / 1024 / 1024:.1f}MB)"
    )
    
    # Upload to Cloudinary
    try:
        upload_result = cloudinary.uploader.upload(
            video.file,
            resource_type="video",
            folder="code_review_walkthroughs",
            public_id=f"submission_{submission_id}_user_{user_id}",
            overwrite=True,
            eager=[{"quality": "auto", "fetch_format": "auto"}],
            eager_async=True,
            timeout=120
        )
        
        video_url = upload_result["secure_url"]
        logger.info(f"Video uploaded successfully: {video_url}")
        
        return video_url
        
    except Exception as e:
        logger.error(f"Cloudinary upload failed: {str(e)}")
        raise ValueError(f"Video upload failed: {str(e)}")


@router.get("", status_code=status.HTTP_200_OK)
def get_submissions(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    status_filter: str = Query(None, description="Filter by status: pending, reviewed"),
    language: str = Query(None, description="Filter by language"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get paginated list of submissions.
    Students see only their own submissions.
    Reviewers/admins see all submissions.
    """
    
    # Base query: submissions + review count
    query = (
        db.query(
            Submission,
            func.count(Review.id).label("review_count")
        )
        .outerjoin(Review, Review.submission_id == Submission.id)
        .group_by(Submission.id)
    )

    # Student: only own submissions
    if current_user.role == "student":
        query = query.filter(Submission.user_id == current_user.id)

    # Apply filters
    if status_filter:
        query = query.filter(Submission.status == status_filter)
    
    if language:
        query = query.filter(Submission.language == language)

    total = query.count()

    # Apply pagination
    results = query.offset(skip).limit(limit).all()

    submissions = []
    for submission, review_count in results:
        if current_user.role == "student":
            submissions.append({
                "id": submission.id,
                "title": submission.title,
                "language": submission.language,
                "status": submission.status,
                "created_at": submission.created_at,
                "review_count": review_count
            })
        else:
            submissions.append({
                "id": submission.id,
                "user": {
                    "id": submission.user.id,
                    "name": submission.user.name
                },
                "title": submission.title,
                "language": submission.language,
                "status": submission.status,
                "created_at": submission.created_at,
                "review_count": review_count
            })

    return {
        "submissions": submissions,
        "total": total,
        "page": (skip // limit) + 1,
        "pages": (total + limit - 1) // limit,
        "showing": len(submissions)
    }


@router.get("/{id}")
def get_submission(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a single submission by ID with all related data."""
    
    # Eager load related data to avoid N+1 queries
    submission = (
        db.query(Submission)
        .options(
            joinedload(Submission.user),
            joinedload(Submission.tags),
            joinedload(Submission.reviews).joinedload(Review.reviewer),
            joinedload(Submission.reviews).joinedload(Review.annotations)
        )
        .filter(Submission.id == id)
        .first()
    )

    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    if current_user.role == "student" and submission.user_id != current_user.id:
        logger.warning(
            f"User {current_user.id} attempted to access submission {id} "
            f"but is not the owner."
        )
        raise HTTPException(status_code=403, detail="Not authorized")

    return serialize_submission(submission)


@router.put("/{id}", response_model=SubmissionResponse)
def update_submission(
    id: int,
    payload: SubmissionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a pending submission. Only the owner can update."""
    
    submission = db.query(Submission).filter(Submission.id == id).first()

    # Check existence FIRST
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found.")

    # Ownership check
    if submission.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to update this submission."
        )

    # Status check
    if submission.status != "pending":
        raise HTTPException(
            status_code=400,
            detail="Only pending submissions can be updated."
        )

    # Update ONLY provided fields
    if payload.title is not None:
        submission.title = payload.title

    if payload.description is not None:
        submission.description = payload.description

    if payload.code_content is not None:
        submission.code_content = payload.code_content

    # Persist changes
    db.commit()
    db.refresh(submission)
    
    logger.info(f"Submission {id} updated by user {current_user.id}")

    return submission


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_submission(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a pending submission. Only the owner can delete."""
    
    submission = db.query(Submission).filter(Submission.id == id).first()

    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found.")

    if submission.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to delete this submission."
        )

    if submission.status != "pending":
        raise HTTPException(
            status_code=400,
            detail="Only pending submissions can be deleted."
        )

    db.delete(submission)
    db.commit()
    
    logger.info(f"Submission {id} deleted by user {current_user.id}")
    
    return