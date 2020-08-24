import os
import re

def get_file_path(root_path,file_list,dir_list):
    #获取该目录下所有的文件名称和目录名称
    dir_or_files = os.listdir(root_path)
    for dir_file in dir_or_files:
        #获取目录或者文件的路径
        dir_file_path = os.path.join(root_path,dir_file)
        #判断该路径为文件还是路径
        if os.path.isdir(dir_file_path):
            dir_list.append(dir_file_path)
            #递归获取所有文件和目录的路径
            get_file_path(dir_file_path,file_list,dir_list)
        else:
            file_list.append(dir_file_path)

def replace(line, md_tag, html_tag_1, html_tag_2):
    ishead = True
    while(1):
        if(line.find(md_tag) == -1):
            return line
        if(ishead):
            line = line.replace(md_tag, html_tag_1, 1)
        else:
            line = line.replace(md_tag, html_tag_2, 1)
        ishead = not ishead

def replaceultag(f_md_lines):
    ulbodylayer = 0
    for i in range(0, len(f_md_lines)):
        headmark = re.match(r"^\*+", f_md_lines[i])
        if(headmark != None):
            headmarkgrade = headmark.span()[1]
        else:
            headmarkgrade = 0
        if(ulbodylayer < headmarkgrade):
            f_md_lines[i] = "<ul>\n<li>" + (f_md_lines[i][headmarkgrade+1:]).rstrip('\n') + "</li>\n"
            ulbodylayer = ulbodylayer + 1
        elif(ulbodylayer > headmarkgrade):
            f_md_lines[i-1] = f_md_lines[i-1] + "</ul>\n"
            ulbodylayer = ulbodylayer - 1
        else:
            if(ulbodylayer != 0):
                f_md_lines[i] = "<li>" + (f_md_lines[i][headmarkgrade+1:]).rstrip('\n') + "</li>\n"

def replaceheadtag(f_md_lines, headtag):
    layer = 0
    tmplist = []
    for i in range(0, len(f_md_lines)):
        headmark = re.match("^#+", f_md_lines[i])
        if(headmark != None):
            headmarkgrade = headmark.span()[1]
            tmpstr = "<h" + str(headmarkgrade) + ">" + (f_md_lines[i][headmarkgrade+1:]).rstrip('\n') + "</h" + str(headmarkgrade) + ">" + "<a name=\"" + (f_md_lines[i][headmarkgrade+1:]).rstrip('\n') +"\"></a>" + "\n"
            tmplist.append([headmarkgrade, (f_md_lines[i][headmarkgrade+1:]).rstrip('\n')])
            f_md_lines[i] = tmpstr
    for item in range(0, len(tmplist)):
        if(layer < tmplist[item][0]):
            headtag.append("<ul>\n<li class=\"bookmark"+str(tmplist[item][0])+"\">" + "<a href=\"javascript:gotopos('" + tmplist[item][1] +"')\">" + tmplist[item][1] + "</a></li>\n")
            layer = layer + 1
        elif(layer > tmplist[item][0]):
            headtag[len(headtag)-2] = headtag[len(headtag)-2] + "</ul>\n"
            layer = layer - 1
        else:
            if(layer != 0):
                headtag.append("<li class=\"bookmark"+str(tmplist[item][0])+"\">" + "<a href=\"javascript:gotopos('" + tmplist[item][1] +"')\">" + tmplist[item][1] + "</a></li>\n")
    while(layer != 0):
        headtag.append("</ul>\n")
        layer = layer - 1
        

def replaceparagraph(f_md_lines):
    for i in range(0, len(f_md_lines)):
        headmark = re.match("^<+", f_md_lines[i])
        if(headmark == None):
            f_md_lines[i] = "<p>"+f_md_lines[i].rstrip('\n')+"</p>\n"

if __name__ == "__main__":
    #根目录路径
    root_path = r"./content"
    #用来存放所有的文件路径
    file_list = []
    #用来存放所有的目录路径
    dir_list = []
    get_file_path(root_path,file_list,dir_list)
    print(file_list)
    print(dir_list)
    for dir in dir_list:
        os.makedirs(dir[10:], exist_ok=True)

    for mode in ["lightstyle", "darkstyle"]:
        css_template = open("./pyscript/styletemplate.css", mode='r', encoding="utf-8")
        css_template_lines = css_template.readlines()
        css_template.close()

        css_conf = open("./pyscript/"+mode+".conf", mode='r', encoding="utf-8")
        css_conf_lines = css_conf.readlines()
        css_conf.close()
        replace_dict = {}

        for i in css_conf_lines:
            tmpls = i.split(": ")
            replace_dict[tmpls[0]] = tmpls[1].strip()

        css_output = open(mode+".css", mode='w', encoding="utf-8")
        for string in css_template_lines:
            replacemark = re.search(r"\!([\d\D]*)\!", string)
            if(replacemark != None):
                string = string.replace(str(replacemark.group()), replace_dict[str(replacemark.group())])
            css_output.write(string)
        css_output.close()

    h_template = open("./pyscript/template.html", mode='r', encoding="utf-8")
    h_template_lines = h_template.readlines()
    insertindex = -1
    categoryindex = -1
    for i in range(0, len(h_template_lines)-1):
        insertmark = re.search("maintext", h_template_lines[i])
        if(insertmark != None):
            insertindex = i
        categorymark = re.search("categorycontent", h_template_lines[i])
        if(categorymark != None):
            categoryindex = i
    h_template.close()

    for file in file_list:
        f_html = open((file[10:-3]+".html"), mode='w+', encoding="utf-8")

        for i in range(0, insertindex+1):
            f_html.write(h_template_lines[i])

        f_md = open(file, mode='r', encoding="utf-8")
        f_md_lines = f_md.readlines()

        headtag = []

        replaceheadtag(f_md_lines, headtag)
        replaceultag(f_md_lines)

        replaceparagraph(f_md_lines)
        
        for i in range(0, len(f_md_lines)):
            f_md_lines[i] = replace(f_md_lines[i], "~~", "<del>", "</del>")

        f_md.close()

        for i in f_md_lines:
            f_html.write(i)
        
        for i in range(insertindex+1, categoryindex+1):
            f_html.write(h_template_lines[i])

        for i in headtag:
            f_html.write(i)
        
        for i in range(categoryindex+1, len(h_template_lines)-1):
            f_html.write(h_template_lines[i])

        f_html.close()