#!/usr/bin/env python3
import sys
import socket
import string
import os
from datetime import datetime, timedelta
import time
import configparser
import pickle

config = configparser.ConfigParser()
config.read('config.ini')

debug = True

config = {
    'host': config.get('irc', 'host'),
    'port': config.getint('irc', 'port'),
    'nick': config.get('irc', 'nick'),
    'pass': config.get('irc', 'pass'),
    'chan': config.get('irc', 'chan'),
}

irc_socket = None

irc_timeout = 5 * 60

mods = set([''])

data = {}

def log_info(s):
    print('[i] {}'.format(s))

def log_debug(s):
    if debug:
        print('[d] {}'.format(s))

def print_startup_message():
    log_info('{} starting up!'.format(os.path.basename(__file__)))

def init_socket():
    global irc_socket
    irc_socket = connect_to_irc()

def init_data():
    global data
    data = {
        'bets': {},
        'last_persist': datetime.utcnow(),
        'betstart_time': None,
        'betend_time': None,
        'final_time': None,
        'bet_warned': False,
    }

def irc_send(string):
    sock = irc_socket
    log_debug('sending: {}'.format(string))
    sock.send(bytes(string + '\r\n', 'utf-8'))

def auth_and_join():
    log_info('joining {} as {}'.format(config['chan'], config['nick']))
    irc_send('CAP REQ :twitch.tv/membership')
    irc_send('PASS {}'.format(config['pass']))
    irc_send('NICK {}'.format(config['nick']))
    irc_send('JOIN #{}'.format(config['chan']))

def connect_to_irc():
    log_info('connecting to irc with a new socket')
    sock = socket.socket()
    sock.settimeout(irc_timeout)
    sock.connect((config['host'], config['port']))
    log_info('new irc socket connected')
    return sock

def send_pong(segs):
    hostname = segs[1]
    irc_send('PONG {}'.format(hostname))

def send_msg(message):
    irc_send('PRIVMSG #{} :/me {}'.format(config['chan'], message))

# this isn't working right now, spam prevention maybe?
def send_whisper(sender, message):
    irc_send('PRIVMSG #{} :/w {} {}'.format(config['chan'], sender, message))

def parse_time(message):
    time_segs = message.split(':')
    if not (len(time_segs) <= 4 and len(time_segs) >= 2):
        return None
    hours, minutes, seconds, milliseconds = (0, 0, 0, 0)
    try:
        # strptime doesn't support 25+ hours (for something like BotW hundo)
        # yes this logic tree is madness
        if len(time_segs) == 4:
            hours = int(time_segs[0])
            minutes = int(time_segs[1])
            seconds = int(time_segs[2])
            if len(time_segs[3]) > 3:
                raise ValueError()
            elif len(time_segs[3]) == 1:
                milliseconds = int(time_segs[3]) * 100
            elif len(time_segs[3]) == 2:
                milliseconds = int(time_segs[3]) * 10
            elif len(time_segs[3]) == 3:
                milliseconds = int(time_segs[3])
        if len(time_segs) == 3:
            hours = int(time_segs[0])
            minutes = int(time_segs[1])
            second_segs = time_segs[2].split('.')
            if len(second_segs) == 2:
                seconds = int(second_segs[0])
                if len(second_segs[1]) > 3:
                    raise ValueError()
                elif len(second_segs[1]) == 1:
                    milliseconds = int(second_segs[1]) * 100
                elif len(second_segs[1]) == 2:
                    milliseconds = int(second_segs[1]) * 10
                elif len(second_segs[1]) == 3:
                    milliseconds = int(second_segs[1])
            else:
                seconds = int(second_segs[0])
        if len(time_segs) == 2:
            minutes = int(time_segs[0])
            second_segs = time_segs[1].split('.')
            if len(second_segs) == 2:
                seconds = int(second_segs[0])
                if len(second_segs[1]) > 3:
                    raise ValueError()
                elif len(second_segs[1]) == 1:
                    milliseconds = int(second_segs[1]) * 100
                elif len(second_segs[1]) == 2:
                    milliseconds = int(second_segs[1]) * 10
                elif len(second_segs[1]) == 3:
                    milliseconds = int(second_segs[1])
            else:
                seconds = int(second_segs[0])
    except ValueError:
        return None
    try:
        delta = timedelta(
            hours=hours,
            minutes=minutes,
            seconds=seconds,
            milliseconds=milliseconds)
    except:
        return None
    return delta

def echo(sender, message):
    if sender not in mods:
        return

    send_msg(message)

def wecho(sender, message):
    if sender not in mods:
        return

    send_whisper(sender, message)

def startbets(sender, message):
    if sender not in mods:
        return

    global data
    delta = parse_time(message)
    if not delta:
        send_msg('@{} '
                 'invalid time format for !startbets. '
                 'Use h:mm:ss.ms'.format(sender))
        return
    init_data()
    data['betstart_time'] = datetime.utcnow()
    data['betend_time'] = datetime.utcnow() + delta
    send_msg('Betting is open! PogChamp Place your bets with !bet')

def bet(sender, message):
    betend_time = data.get('betend_time')
    if not betend_time:
        send_msg('@{} there\'s no active run to bet on'.format(sender))
        return

    if datetime.utcnow() > data.get('betend_time'):
        send_msg('@{} betting has ended for this run'.format(sender))
        return

    delta = parse_time(message)
    if not delta:
        send_msg('@{} '
                 'invalid time format for !bet. '
                 'Use h:mm:ss.ms'.format(sender))
        return

    # bets are tuples of (bet_time, bet)
    data['bets'][sender] = (datetime.utcnow(), delta)

def compute_score(final_time, lateness, inaccuracy):
    score = ((final_time - (((lateness**2) / final_time) / 8) - inaccuracy) / final_time) * 100000
    return max(round(score, 3), 0)

def format_delta(delta):
    delta = str(delta)
    delta_segs = delta.split('.')
    if len(delta_segs) == 1:
        return delta_segs[0]
    else:
        return '{}.{}'.format(delta_segs[0], delta_segs[1][:2])

def winners(sender, message):
    if sender not in mods:
        return

    betend_time = data.get('betend_time')
    if not betend_time:
        send_msg('@{} there\'s no active run'.format(sender))
        return

    final_time = data.get('final_time')
    if not final_time:
        send_msg('@{} the final time has not been set'.format(sender))
        return

    results = []
    betstart_time = data['betstart_time']
    for user in data['bets']:
        user_bet_time = data['bets'][user][0]
        user_bet = data['bets'][user][1]

        lateness_delta = user_bet_time - betstart_time
        lateness = abs((lateness_delta).total_seconds())
        inaccuracy = abs((user_bet - final_time).total_seconds())

        score = compute_score(final_time.total_seconds(), lateness, inaccuracy)

        results.append((score, user, user_bet, lateness_delta))

    results = sorted(results)
    results.reverse()

    if len(results) < 1:
        send_msg('@{} there were no bets'.format(sender))
        return

    results_file = open('results_{}'.format(str(betstart_time)), 'w')
    results_file.write('{}, {}, {}\n'.format(str(final_time), str(betstart_time), str(betend_time)))
    for result in results:
        results_file.write('{}, {}, {}, {}\n'.format(
            str(result[1]),
            str(result[0]),
            str(result[2]),
            str(result[3])))
    results_file.close()

    winning_bets = results[:5]

    formatted_winners = []
    for bet in winning_bets:
        formatted_winners.append('{}: {} ({} at {})'.format(
            bet[1], bet[0], format_delta(str(bet[2])), format_delta(str(bet[3]))))
    winners = ''
    for i, winner in enumerate(formatted_winners):
        winners += '{}. {} '.format(i + 1, winner)

    send_msg(winners)

def finaltime(sender, message):
    if sender not in mods:
        return

    global data

    betend_time = data.get('betend_time')
    if not betend_time:
        send_msg('@{} there\'s no active run'.format(sender))
        return

    if datetime.utcnow() < betend_time:
        data['betend_time'] = datetime.utcnow()

    delta = parse_time(message)
    if not delta:
        send_msg('@{} '
                 'invalid time format for !finaltime. '
                 'Use h:mm:ss.ms'.format(sender))
        return
    data['final_time'] = delta
    send_msg('The final time for the run is {}!'.format(format_delta(delta)))
    winners(sender, message)

def checkbet(sender, message):
    bet = data['bets'].get(sender)
    if not bet:
        return
    send_msg('@{} Your current bet is {} (at {})'.format(
        sender, format_delta(bet[1]),
        format_delta(bet[0] - data['betstart_time'])))
    
def betcount(sender, message):
    if sender not in mods:
        return
    send_msg('The current amount of bets is: {}!'.format(len(data['bets'])))
    
commands = {
    'echo': echo,
    'wecho': wecho,
    'startbets': startbets,
    'bet': bet,
    'winners': winners,
    'finaltime': finaltime,
    'checkbet': checkbet,
    'betcount': betcount,
}

def process_message(segs):
    sender = segs[0].split('!')[0].lstrip(':').strip()
    message = segs[3].lstrip(':').strip()

    if message.startswith('!'):
        message = message.split(maxsplit=1)
        command = message[0].lstrip('!')
        if len(message) > 1:
            message = message[1]
        else:
            message = ''
        if commands.get(command):
            commands[command](sender, message)

def store_mods(segs):
    global mods
    info = segs[3].split()
    if info[0] == '+o':
        mods.add(info[1])

def process_line(segs):
    if segs[0] == 'PING':
        send_pong(segs) 
    if segs[1] == 'PRIVMSG':
        process_message(segs)
    if segs[1] == 'MODE':
        store_mods(segs)

def bet_warning():
    global data

    if data.get('bet_warned'):
        return

    betend_time = data.get('betend_time')
    if not betend_time:
        return

    to_end = (betend_time - datetime.utcnow()).total_seconds()
    if to_end > 0 and to_end < 30:
        send_msg('30 seconds left to bet!')
        data['bet_warned'] = True

def auto_sends():
    bet_warning()

def persist_data():
    global data
    last_persist = data['last_persist']
    if (datetime.utcnow() - last_persist).total_seconds() > 10:
        log_debug("persisting data now")
        autosave = open('autosave', 'wb')
        pickle.dump(data, autosave)
        autosave.close()
        data['last_persist'] = datetime.utcnow()

def load_data():
    global data
    try:
        autosave = open('autosave', 'rb')
        data = pickle.load(autosave)
        log_info('data loaded successfully')
    except:
        init_data()

def periodic():
    persist_data()

def start_irc():
    init_socket()
    auth_and_join()

def bot_loop():
    sock = irc_socket
    readbuffer = ""
    while True:
        try:
            readbuffer = readbuffer + sock.recv(4096).decode('utf-8')
            lines = [line.strip() for line in readbuffer.split('\n')]
            readbuffer = lines.pop()

            for line in lines:
                log_debug(line)
                segs = line.split(maxsplit=3)
                process_line(segs)

            auto_sends()
            periodic()
        except socket.timeout:
            start_irc()
            sock = irc_socket
            readbuffer = ""

def main():
    print_startup_message()
    load_data()
    start_irc()
    bot_loop()

if __name__ == "__main__":
    main()
