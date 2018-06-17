from opsdroid.matchers import match_regex
import logging
import random
import re
import datetime
import time
import subprocess
import os
import aiohttp

def setup(opsdroid):
    logging.debug("Loaded shell module")

def get_code_text(text):
  return "<pre><code>"+text+"</code></pre>"

@match_regex(r'Please run (?P<command>.*)$')
async def do_something(opsdroid, config, message):
    scriptdir=config.get("scriptdir","~/.opsdroid/modules/opsdroid-modules/skill/shell/script/")
    inittalkbacktimeout=config.get("initialtalkbacktimeout",5)
    talkbacktimeout=config.get("talkbacktimeout",15)
    argsep=config.get("argumentumseparator",";")
    msg=message.regex.group("command")
    if not msg:
      return True
    cmd=msg.split(argsep)
    if '..' in cmd[0]:
      return True
    command=cmd[0]
    cmd[0]=os.path.join(scriptdir,cmd[0])
    if not os.path.isfile(cmd[0]):
      return True

    #
    # Execute the script
    # ##################
    try:
      logging.info("Doing (("+str(cmd)+"))")
      w=datetime.datetime.now()+datetime.timedelta(seconds=inittalkbacktimeout)
      starttime=datetime.datetime.now()
      res=subprocess.Popen(cmd,
                           cwd=str(scriptdir),
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE,
                           close_fds=True,
                           bufsize=0,
                           universal_newlines=True,
                           )
      stdout="Starting the script named "+str(command)+" on "+str(datetime.datetime.now())+"...<br/>\nPlease be patient...<br/>\n"
      try:
        await message.respond(str(stdout))
      except aiohttp.client_exceptions.ServerDisconnectedError:
        import traceback
        logging.error("Error while running script: "+str(traceback.format_exc()))
        time.sleep(3)
        logging.error("== Retry ==")
        await message.respond(str(stdout))
        logging.error("== Recovered ==")
      stdout=u""
      stderr=u""
      #
      # Time to time put some feedback to the matrix room
      # ##################################################
      while ( res.poll() == None ):
        stdout+=res.stdout.readline()
        if w<=datetime.datetime.now():
          try:
            await message.respond(get_code_text(str(stdout)))
          except aiohttp.client_exceptions.ServerDisconnectedError:
            import traceback
            logging.error("Error while running script: "+str(traceback.format_exc()))
            time.sleep(3)
            logging.error("== Retry ==")
            await message.respond(get_code_text(str(stdout)))
            logging.error("== Recovered ==")
          w=datetime.datetime.now()+datetime.timedelta(seconds=talkbacktimeout)
          stdout=""
        time.sleep(1)

      (stdoutplus,stderrplus)=res.communicate()
      stdout+=str(stdoutplus)
      stderr+=str(stderrplus)
      logging.info("Done (("+str(cmd)+"))")
    except Exception:
      import traceback
      logging.error("Error while running script: "+str(traceback.format_exc()))
      await message.respond(get_code_text(str(stdout))+ \
        "<br/>\n There was an error while running the script"+ \
        " for more details")
      stdout=""
    #
    # Finally put the last messages to the chat
    # ##########################################
    stdout=get_code_text(stdout)
    if len(stderr)>0:
      stdout+="\nThe "+str(command)+ \
        " command sent messages to the error output also."+ \
        " See bellow:<br/>\n"+get_code_text(str(stderr))
    send_out=str(stdout)+ \
        "\nThe command "+str(command)+ \
        " ended with the return code of "+str(res.returncode)+" on "+ \
        str(datetime.datetime.now())+ \
        " and was running "+str(datetime.datetime.now()-starttime)+ \
        " seconds long."
    try:
      await message.respond(str(send_out))
    except aiohttp.client_exceptions.ServerDisconnectedError:
      import traceback
      logging.error("Error while sending: "+str(traceback.format_exc()))
      time.sleep(3)
      logging.error("== Retry ==")
      await message.respond(str(send_out))
      logging.error("== Recovered ==")
      
