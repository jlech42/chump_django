def TranslateTopicButtonToTag(button_name):
    tag_name = ''
    translate_dict = {}
    translate_dict['Relaxation'] = 'Relax and unwind'
    translate_dict['Truth'] = 'Learn the truth'
    translate_dict['Education'] = 'Learn something'
    translate_dict['Mystery'] = 'Explore the mystery'
    translate_dict['Art'] = 'Experience Art'
    translate_dict['Worldview'] = 'Broaden your perspective'
    for key, value in translate_dict.items():
        if button_name == key:
            return value
    return tag_name

def get_count_of_gallery_elements(chatfuel_response):
    count = len(chatfuel_response['messages'][0]['attachment']['payload']['elements'])
    return count
