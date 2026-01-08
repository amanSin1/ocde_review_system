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

from app.api.routes.helpers import serialize_submission

router = APIRouter(
    prefix = "/api/submissions",
    tags = ["Submissions"]
)

@router.post("/", status_code = status.HTTP_201_CREATED)
def create_submission(payload: SubmissionCreate, db : Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "student":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only students can create submissions.")
    submission = Submission(
        user_id = current_user.id,
        title = payload.title,
        description = payload.description,
        code_content = payload.code_content,
        language = payload.language
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)

    tag_names = []
    for tag_name in payload.tags:
        tag = db.query(Tag).filter(Tag.name == tag_name).first()
        if not tag:
            tag = Tag(name = tag_name)
            db.add(tag)
            db.commit()
            db.refresh(tag)
        link = SubmissionTag(submission_id = submission.id, tag_id = tag.id)
        db.add(link)
        tag_names.append(tag.name)
    db.commit()
    return{
        "id" : submission.id,
        "user_id" : submission.user_id,
        "title" : submission.title,
        "description" : submission.description,
        "code_content" : submission.code_content,
        "language" : submission.language,
        "status" : submission.status,
        "tags" : tag_names,
        "created_at" : submission.created_at,
    }



@router.get("/", status_code=status.HTTP_200_OK)
def get_submissions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
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

    results = query.all()

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
        "total": len(submissions),
        "page": 1,
        "pages": 1
    }


@router.get("/{id}")
def get_submission(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    submission = db.query(Submission).filter(
        Submission.id == id
    ).first()

    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    if current_user.role == "student" and submission.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    return serialize_submission(submission)


@router.put("/{id}", response_model=SubmissionResponse, status_code=status.HTTP_200_OK)
def update_submission(
    id: int,
    payload: SubmissionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    submission = db.query(Submission).filter(Submission.id == id).first()

    # Check existence FIRST
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found.")

    # Ownership check
    if submission.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this submission.")

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

    return submission

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_submission(id:int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    submission = db.query(Submission).filter(Submission.id == id).first()

    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found.")

    if submission.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this submission.")

    if submission.status != "pending":
        raise HTTPException(status_code=400, detail="Only pending submissions can be deleted.")

    db.delete(submission)
    db.commit()
    return
