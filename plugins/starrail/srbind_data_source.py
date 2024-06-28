from io import BytesIO

import qrcode
from sqlalchemy import select, update
from ..orm import get_session  # 确保已经从数据库插件中导入这个方法

from .srbind_model import UserBind

async def set_user_srbind(user: UserBind) -> None:
    select_user = await get_user_srbind(user.bot_id, user.user_id)
    update_flag = False
    for old_user in select_user:
        if user.user_id != "0":
            # not public user
            if user.sr_uid != old_user.sr_uid:
                # delete origin user
                async with get_session() as session:
                    await old_user.delete(using_db=session)
            else:
                # update user
                old_user.mys_id = user.mys_id
                old_user.device_id = user.device_id
                old_user.device_fp = user.device_fp
                old_user.cookie = user.cookie
                old_user.stoken = user.stoken
                async with get_session() as session:
                    await old_user.save(using_db=session)
                update_flag = True
        else:
            # public user
            if user.cookie == old_user.cookie:
                old_user.mys_id = user.mys_id
                old_user.device_id = user.device_id
                old_user.device_fp = user.device_fp
                old_user.cookie = user.cookie
                old_user.stoken = user.stoken
                async with get_session() as session:
                    await old_user.save(using_db=session)
                update_flag = True
    if not update_flag:
        async with get_session() as session:
            await user.save(using_db=session)

async def del_user_srbind(bot_id: str, user_id: str, sr_uid: str) -> None:
    select_user = await get_user_srbind(bot_id, user_id)
    select_uid = [user.sr_uid for user in select_user]
    if sr_uid in select_uid:
        user = select_user[select_uid.index(sr_uid)]
        async with get_session() as session:
            await user.delete(using_db=session)

async def get_user_srbind(bot_id: str, user_id: str) -> list[UserBind]:
    return await UserBind.filter(user_id=user_id).all()
    #return await UserBind.filter(bot_id=bot_id, user_id=user_id).all()
    # 这里的屎以后再修

def generate_qrcode(url: str) -> BytesIO:
    qr = qrcode.QRCode(  # type: ignore
        version=1, error_correction=qrcode.ERROR_CORRECT_L, box_size=10, border=4
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    bio = BytesIO()
    img.save(bio)
    return bio
