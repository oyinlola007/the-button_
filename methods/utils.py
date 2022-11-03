from pyfiglet import Figlet

import methods.config as config

def convert_elapsed(elapsed):
    m, s = divmod(config.DURATION - elapsed, 60)
    text = " ".join('{:02d}:{:02d}'.format(m, s))
    return render_text(text, config.FONT)

def render_text(text, font):
    custom_fig = Figlet(font=font)
    return custom_fig.renderText(text)