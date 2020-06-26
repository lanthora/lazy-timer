import configparser
import json
import signal
import sys
from functools import wraps
from time import localtime, strftime, time

from telegram import Bot
from telegram.ext import CommandHandler, Updater

from lazytimer import LazyTimer


def absolute_path(relative_path: str) -> str:
    return "{}/{}".format(sys.path[0], relative_path)


def default(default_value):
    def set_default_value(fn):
        @wraps(fn)
        def decorated(*args, **kwargs):
            try:
                ret = fn(*args, **kwargs)
            except:
                ret = default_value
                logging.debug("函数 {} 使用默认返回值 {}".format(
                    fn.__name__, default_value))
            finally:
                return ret
        return decorated
    return set_default_value


def singleton(cls):
    _instance = {}

    def inner():
        if cls not in _instance:
            _instance[cls] = cls()
        return _instance[cls]
    return inner


@singleton
class NoSQLDB(object):
    def __init__(self):
        self.data: dict = {}
        self.__loaded: bool = False
        self.__dumped: bool = False

    def load(self):
        if self.__loaded:
            return
        self.__loaded = True
        self.data = self.__restore(absolute_path("database.json"))

    @default({})
    def __restore(self, path):
        logging.info("加载数据")
        with open(path, "r", encoding="UTF-8") as f:
            return json.load(f)

    def dump(self):
        if(self.__dumped):
            return
        self.__dumped = True

        logging.info("保存数据")
        with open(absolute_path("database.json"), "w", encoding="UTF-8") as f:
            json.dump(self.data, f, ensure_ascii=False)

    def get_user_delay_db(self):
        self.load()
        return self.data.setdefault("user_delay", {})


class MoyuBot:
    def __init__(self):
        self.__config = configparser.ConfigParser()
        self.__config.read('conf.ini')
        self.__token = self.__config.get("default", "token")
        self.bot = Bot(self.__token)
        self.updater = Updater(token=self.__token, use_context=True)
        self.dp = self.updater.dispatcher
        self.dic = NoSQLDB().get_user_delay_db()
        self.__lazytimer = LazyTimer()
        signal.signal(signal.SIGINT, self.sig_handler)
        signal.signal(signal.SIGTERM, self.sig_handler)

    def __send_html(self, chat_id, text):
        self.bot.send_message(
            chat_id, text,
            parse_mode='HTML',
            disable_web_page_preview=True
        )

    def __error(self, update, context):
        try:
            raise context.error
        except BaseException as e:
            pass

    def __check_in(self, chat_id):
        text = strftime("【<b>上班打卡</b>】 %H:%M", localtime())
        self.__send_html(chat_id, text)

    def __check_out(self, chat_id):
        text = strftime("【<b>下班提醒</b>】 %H:%M", localtime())
        self.__send_html(chat_id, text)

    def checkin(self, update, context):
        chat_id = update.message.chat_id
        delay: int = 0
        try:
            # 输入小时，在代码级别转化成秒
            def info(cmd): return [i for i in cmd.split(' ') if i != '']
            delay = 3600*float(info(update.message.text)[1])
            self.dic[chat_id] = delay
            NoSQLDB().dump()
        except IndexError:
            try:
                delay = self.dic[chat_id]
            except KeyError:
                self.__send_html(chat_id, "没有保存的打卡记录，请使用完整命令")
                return
            except:
                raise Exception()
        except:
            self.__send_html(chat_id, "打卡时发生了开发人员不想解决的错误")
            return

        self.__lazytimer.add(time()+delay, self.__check_out, [chat_id])
        self.__check_in(chat_id)

    def run(self):
        self.dp.add_handler(CommandHandler('checkin', self.checkin))
        self.dp.add_error_handler(self.__error)
        self.updater.start_polling()

    def sig_handler(self, signal, frame):
        NoSQLDB().dump()
        self.updater.stop()
