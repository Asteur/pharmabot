import xml.etree.ElementTree as ET

namespace = '{urn:schemas-microsoft-com:office:spreadsheet}'

def tag_name(tag):
    '''
    produce tag_name
    :param tag: xml tag,
    :param namespace:
    :return: tag_name
    '''
    tag_name = namespace + tag
    return tag_name


tree = ET.parse('drugscomQA200.xml')

# tag names:
tag_name_content = tag_name('Worksheet') + '/' + tag_name('Table') + '/' + tag_name('Row') + '/' + tag_name('Cell') + '/' + tag_name('Data')

# get the elems (or xml objects):
elems = tree.findall(tag_name_content)
# print(elems)

# get content from the tags:
f = 'unknown_words.txt'
specials = ['?','.','!','"','...',')','(',';']
long_word_list = []
for elem in elems:
    if elem.text.startswith('https') == False:
        words_list = elem.text.split(' ')
        # print(words_list)
        for i in words_list:
            if i in specials:
                if i not in long_word_list:
                    # print(i)
                    long_word_list.append(i)

            else:
                if i not in long_word_list:
                    new_i = i.replace(',','').replace('?','').replace('.','').replace('!','').replace('"','').replace('...','').replace('(','').replace(';','')
                    # print(new_i)
                    long_word_list.append(new_i)

with open(f,'+a', encoding='utf-8') as content:
    final_list = []
    for i in long_word_list:
        if i not in final_list:
            final_list.append(i)
            content.write('%s\n' % i)

print(len(final_list))
print(final_list)








