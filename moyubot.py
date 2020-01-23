import configparser
from lazytimer import LazyTimer
from telegram import Bot
from telegram.ext import CommandHandler, Updater
from time import time,strftime,localtime

class MoyuBot:
    def __init__(self):
        self.__config = configparser.ConfigParser()
        self.__config.read('conf.ini')
        self.__token = self.__config.get("default", "token")
        self.bot = Bot(self.__token)
        self.updater = Updater(token=self.__token, use_context=True)
        self.dp = self.updater.dispatcher
        self.dic = {}
        self.__lazytimer = LazyTimer()
        
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

    def __check_in(self,chat_id):
        text = strftime("【<b>上班打卡</b>】 %H:%M:%S", localtime())
        self.__send_html(chat_id,text)

    def __check_out(self,chat_id):
        text = strftime("【<b>下班提醒</b>】 %H:%M:%S", localtime())
        self.__send_html(chat_id,text)

    def checkin(self, update, context):
        chat_id = update.message.chat_id
        delay:int = 0
        try:
            # 输入小时，在代码级别转化成秒
            delay = 3600*float(update.message.text.split(' ')[1])
            self.dic[chat_id] = delay
        except IndexError:
            try:
                delay = self.dic[chat_id]
            except KeyError:
                self.__send_html(chat_id,"没有保存的打卡记录，请使用完整命令")
                return
            except:
                raise Exception()
        except:
            self.__send_html(chat_id,"打卡时发生了开发人员不想解决的错误")
            return

        self.__lazytimer.add(time()+delay,self.__check_out,[chat_id])
        self.__check_in(chat_id)

    def run(self):
        self.dp.add_handler(CommandHandler('checkin', self.checkin))
        self.dp.add_error_handler(self.__error)
        self.updater.start_polling()