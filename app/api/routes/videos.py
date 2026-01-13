# app/api/routes/videos.py
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, status
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader
from app.database import get_db
from app.oauth2 import get_current_user
from app.models.user import User
from app.models.submission import Submission
from app.config import settings
from app.core.logger import logger

router = APIRouter(prefix="/api/submissions", tags=["Videos"])

# Configure Cloudinary
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True
)

@router.post("/upload-video", status_code=status.HTTP_200_OK)
async def upload_walkthrough_video(
    video: UploadFile = File(...),
    submission_id: int = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a walkthrough video for a submission.
    Only the submission owner (student) can upload.
    """
    
    # Verify submission exists
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found"
        )
    
    # Verify user owns this submission
    if submission.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only upload videos for your own submissions"
        )
    
    # Validate file type
    allowed_types = ["video/webm", "video/mp4", "video/quicktime"]
    if video.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_types)}"
        )
    
    # Validate file size (max 100MB)
    video.file.seek(0, 2)  # Move to end of file
    file_size = video.file.tell()
    video.file.seek(0)  # Reset to beginning
    
    max_size = 100 * 1024 * 1024  # 100MB
    if file_size > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large. Maximum size is 100MB"
        )
    
    try:
        logger.info(f"Uploading video for submission {submission_id} by user {current_user.id}")
        
        # Upload to Cloudinary
        upload_result = cloudinary.uploader.upload(
            video.file,
            resource_type="video",
            folder="code_review_walkthroughs",
            public_id=f"submission_{submission_id}_user_{current_user.id}",
            overwrite=True,  # Replace if already exists
            # Optional: Add transformations for optimization
            eager=[
                {"quality": "auto", "fetch_format": "auto"}
            ],
            eager_async=True
        )
        
        logger.info(f"Video uploaded successfully: {upload_result['secure_url']}")
        
        # Save URL to database
        submission.walkthrough_video_url = upload_result["secure_url"]
        db.commit()
        db.refresh(submission)
        
        return {
            "message": "Video uploaded successfully",
            "video_url": upload_result["secure_url"],
            "submission_id": submission_id
        }
    
    except Exception as e:
        logger.error(f"Video upload failed: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload video: {str(e)}"
        )


@router.delete("/{submission_id}/video", status_code=status.HTTP_200_OK)
async def delete_walkthrough_video(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete walkthrough video for a submission.
    Only the submission owner can delete.
    """
    
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found"
        )
    
    if submission.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this video"
        )
    
    if not submission.walkthrough_video_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No video found for this submission"
        )
    
    try:
        # Extract public_id from Cloudinary URL
        public_id = f"code_review_walkthroughs/submission_{submission_id}_user_{current_user.id}"
        
        # Delete from Cloudinary
        cloudinary.uploader.destroy(public_id, resource_type="video")
        
        # Remove URL from database
        submission.walkthrough_video_url = None
        db.commit()
        
        return {"message": "Video deleted successfully"}
    
    except Exception as e:
        logger.error(f"Video deletion failed: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete video: {str(e)}"
        )