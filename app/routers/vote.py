from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from .. import schemas, database, models, oauth2
from sqlalchemy.orm import Session


router = APIRouter(
    prefix="/vote",
    tags=['Vote']
)


@router.post("/", status_code=status.HTTP_201_CREATED)
def vote(vote: schemas.Like, db: Session = Depends(database.get_db),
         current_user: int = Depends(oauth2.get_current_user)):
    find_post = db.query(models.Post).filter(models.Post.id == vote.post_id).first()
    if not find_post:
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {vote.post_id} was not found")
    
    vote_query = db.query(models.likes).filter(models.likes.post_id == vote.post_id, models.User.id == current_user.id)
    found_vote = vote_query.first()

    if (vote.dir == 1):
        if found_vote:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail=f"user {current_user.id} has already liked the post {vote.post_id}")
        
        new_vote = models.likes(post_id=vote.post_id, user_id=current_user.id)
        db.add(new_vote)
        db.commit()
        return {"message": "succesfully liked post"}
    
    else:
        if not found_vote:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="like has already been removed")
        vote_query.delete(synchronize_session=False)
        db.commit()
        return {"message": "succesfully removed like"}

