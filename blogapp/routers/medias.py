from fastapi import UploadFile, File, HTTPException, status, APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from blogapp.models.user import User
from blogapp.models.media import Media
from blogapp.dependencies.user import get_current_user
from blogapp.dependencies.session import get_async_session

router = APIRouter()


@router.post("/media/upload", status_code=201)
async def upload_media(
        file: UploadFile = File(...),
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_session)
):
    """
    Эндпоинт для загрузки медиафайлов.
    """
    # Проверяем размер файла (например, не более 5 MB)
    max_file_size = 5 * 1024 * 1024
    file_body = await file.read()
    if len(file_body) > max_file_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds the limit of 5MB"
        )

    # Сохраняем файл в базу данных
    new_media = Media(
        file_body=file_body,
        file_name=file.filename,
        tweet_id=None  # Медиафайл пока не связан с твитом
    )
    session.add(new_media)
    await session.commit()
    await session.refresh(new_media)

    # Возвращаем ID загруженного файла
    return {"result": True, "media_id": new_media.id}
