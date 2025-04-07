

def format_history(history:list, length = 10):
    history_str = ""
    for message in history[-length:-1]:
        history_str += f"{message['role']}: {message['message']} \n"
    return history_str