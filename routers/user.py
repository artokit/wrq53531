from aiogram import Router, F
from aiogram.filters import Command, KICKED, ChatMemberUpdatedFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ChatMemberUpdated
from config import HELPER_URL
from database.models import User, Stat
import keyboards
import states
import utils

router = Router()


@router.message(Command("start"))
async def start(message: Message):
    is_new_user = User.add_user(message.chat.id, message.chat.username)
    if is_new_user:
        Stat.increment_stat()

    await message.answer('🙋🏻‍♂ Менің есімім Тоғызбай \n ⁃ Жасым 22 де \n ⁃ Айлық табысым 8.000.000 тг\n\n'
                         '◾ Бұл телеграм ботта сіз күнделікті 30.000-нан 80.000 теңгеге дейін табыс таба аласыз✅\n\n'
                         '◾ Мен танымал Онлайн ойын платформаларында өзімнің схемаларыммен ақша табамын !\n\n'
                         '◾ Біз күнделікті ойын талдауына негізделген алгоритмдер мен стратегияларды және Взлом '
                         'системаларды қолданамыз. Олар бізге Ұтысқа шығуға Гарантия береді.\n\n'
                         '🙆🏻‍♂ Схема түсінбеген жағдайда сіздерге “Прямой эфирда” ойнап отырып үйрететін боламын.')
    await utils.send_video(
        message.bot,
        video_name='start.mp4',
        chat_id=message.chat.id,
        reply_markup=keyboards.start.as_markup()
    )


@router.callback_query(F.data == 'about_money')
async def get_about_money_info(call: CallbackQuery):
    await utils.send_video(
        call.bot,
        video_name='about_money.mp4',
        chat_id=call.message.chat.id,
        reply_markup=keyboards.comment_button.as_markup()
    )
    await call.message.answer('Отзывтарды карау ↗')
    await call.message.answer(
        '🙋🏻‍♂ Гарантия берем , Сізді де осындай ұтысқа шығармай қоймаймын. Өзім толықтай '
        'сізге көрсетіп үйретемін 🙏🏻\n\n'
        f'Сразу бастагын келсе маган жаз \"Калай бастаймын\" деп - {HELPER_URL}',
        reply_markup=keyboards.help_button.as_markup()
    )


@router.callback_query(F.data == 'comments')
@router.callback_query(F.data == 'more_comments')
async def get_more_comments(call: CallbackQuery, state: FSMContext):
    await state.set_state(states.SendPhoto.send_photos)
    data = await state.get_data()
    last_photo_id = data.get('last_photo_id', 0)

    if call.data == 'comments' or last_photo_id == 20:
        last_photo_id = 0

    last_messages_comments_ids = data.get('comments')

    if last_messages_comments_ids:
        await utils.safe_delete_media(call.bot, call.message.chat.id, last_messages_comments_ids)

    ids = await send_photos_range(call.bot, call.message.chat.id, last_photo_id+1, last_photo_id+5)
    await state.update_data({'last_photo_id': last_photo_id+5})
    await state.update_data({'comments': ids})


async def send_photos_range(bot, chat_id: int, start_index: int, end_index: int):
    ids = []
    for i in range(start_index, end_index):
        msg = await utils.send_photo(bot, f'{i}.jpg', chat_id=chat_id)
        ids.append(msg.message_id)

    msg = await utils.send_photo(
        bot,
        f'{i+1}.jpg',
        chat_id=chat_id,
        reply_markup=keyboards.more_comments.as_markup()
    )
    ids.append(msg.message_id)

    return ids


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=KICKED))
async def check_bot(event: ChatMemberUpdated):
    Stat.add_block_user(event.chat.id)
