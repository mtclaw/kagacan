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
    while(ulbodylayer != 0):
        f_md_lines[len(f_md_lines)-1] = f_md_lines[len(f_md_lines)-1] + "</ul>\n"
        ulbodylayer = ulbodylayer - 1

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
            headtag.append("</ul>\n<li class=\"bookmark"+str(tmplist[item][0])+"\">" + "<a href=\"javascript:gotopos('" + tmplist[item][1] +"')\">" + tmplist[item][1] + "</a></li>\n")
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

    # make file system structure
    root_path = r"./content"
    file_list = []
    dir_list = []
    get_file_path(root_path,file_list,dir_list)
    for dir in dir_list:
        os.makedirs(dir[10:], exist_ok=True)

    # generate lightstyle.css darkstyle.css
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

    # generate .html

    # read template and find insert point
    h_template = open("./pyscript/template.html", mode='r', encoding="utf-8")
    h_template_lines = h_template.readlines()
    cssindex = -1
    navindex = -1
    insertindex = -1
    categoryindex = -1
    darkpathindex = -1
    for i in range(0, len(h_template_lines)-1):
        cssmark = re.search("<link", h_template_lines[i])
        if(cssmark != None):
            cssindex = i
        navmark = re.search("<nav>", h_template_lines[i])
        if(navmark != None):
            navindex = i
        insertmark = re.search("maintext", h_template_lines[i])
        if(insertmark != None):
            insertindex = i
        categorymark = re.search("categorycontent", h_template_lines[i])
        if(categorymark != None):
            categoryindex = i
        darkpathmark = re.search("var darkpath", h_template_lines[i])
        if(darkpathmark != None):
            darkpathindex = i
    h_template.close()

    # write into .html by line 
    for file in file_list:
        f_html = open((file[10:-3]+".html"), mode='w+', encoding="utf-8")

        # copy from template.html
        for i in range(0, cssindex):
            f_html.write(h_template_lines[i])

        # relative path
        r_path = os.path.dirname((file[10:-3]+".html"))
        if(len(r_path) == 0):
            r_path = "./"
        else:
            r_path = "../../"

        # css <rely on r_path>
        f_html.write(h_template_lines[cssindex].replace("lightstyle.css", r_path + "lightstyle.css"))

        # title <write later>

        # copy from template.html
        for i in range(cssindex+1, navindex+1):
            f_html.write(h_template_lines[i])

        # navbar <rely on r_path> <other link write later>
        navlink = ["index.html", "profile.html"]
        for i in range(1, 3):
            f_html.write(h_template_lines[navindex+i].replace("javascript:void(0)", r_path + navlink[i-1]))

        for i in range(navindex+3, insertindex+1):
            f_html.write(h_template_lines[i])

        # read markdown file
        f_md = open(file, mode='r', encoding="utf-8")
        f_md_lines = f_md.readlines()

        # translate markdowm to html

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

        # category
        for i in headtag:
            f_html.write(i)
        
        for i in range(categoryindex+1, darkpathindex):
            f_html.write(h_template_lines[i])

        # css <rely on r_path>
        f_html.write(h_template_lines[darkpathindex].replace("darkstyle.css", r_path + "darkstyle.css"))
        f_html.write(h_template_lines[darkpathindex+1].replace("lightstyle.css", r_path + "lightstyle.css"))

        for i in range(darkpathindex+2, len(h_template_lines)-1):
            f_html.write(h_template_lines[i])

        f_html.close()