import requests
from bs4 import BeautifulSoup
import pymysql

# link the database
database = pymysql.connect(host='localhost', user='root',
                           passwd='zaoyi...', database="python")
print('数据库连接成功！')
cursor = database.cursor()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.62"}

for page in range(1, 6):
    response = requests.get(f"https://www.qidian.com/rank/hotsales/page{page}/")
    soup = BeautifulSoup(response.text, "html.parser")
    all_info = soup.select('.book-img-text li')
    for info in all_info:
        # 封面
        book_img_url = "https:" + info.find("img").get("src")
        #   print(book_img_url)
        # 标题
        book_title = info.find("h2").string
        #   print(book_title)
        # 作者 类型 连载状态
        author_p = info.find("p", attrs={"class": "author"})
        book_author = author_p.find("a", attrs={"class": "name"}).string
        #  print(book_author)
        book_type = author_p.find("a", attrs={"data-eid": "qd_C42"}).string \
                    + "·" + author_p.find("a", attrs={
            "data-eid": "qd_B61"}).string
        #  print(book_type)
        book_state = author_p.find("span").string
        #   print(book_state)
        # 更新
        update_p = info.find("p", attrs={"class": "update"})
        book_latest_chapter = update_p.find("a", attrs={"data-eid": "qd_C43"}).string
        #  print(book_latest_chapter)
        book_latest_time = update_p.find("span").string
        # print(book_latest_time)
        # 简介
        book_content = info.find("p", attrs={"class": "intro"}).string
        # print(boot_content)

        # Store book ------------------------------------------
        book_detail_url = "https:" + info.find("a", attrs={"class": "red-btn"}).get('href')
        # print(book_detail_url)

        # open the book detail page -----------------------------
        book_detail_soup = BeautifulSoup(requests.get(book_detail_url).text, "html.parser")
        book_detail_a = "https:" + book_detail_soup.find("a", attrs={"data-eid": "qd_G03"}).get('href')
        # print(book_detail_a)

        # open the book read page -------------------------------
        book_read_soup = BeautifulSoup(requests.get(book_detail_a).text, "html.parser")

        # saving's path in mysql
        store_mysql_path = "E:\\\\WebProject\\\\PythonProject\\\\Books\\\\"
        book_store_path_mysql = store_mysql_path + book_title + ".txt"

        # saving's path in local
        store_path = "E:\\WebProject\\PythonProject\\Books\\"
        book_store_free_path = store_path + book_title + ".txt"
        print(
            "小说《" + book_title + "》开始存储到本地,路径为" + book_store_free_path + "-----------------------------------------")
        with open(book_store_free_path, "w+", encoding="utf-8") as f:
            while book_read_soup is not None and book_read_soup.find("div", attrs={"class": "vip-limit-wrap"}) is None:
                # the chapter name
                chapter_name = book_read_soup.find("h3", attrs={"class": "j_chapterName"})
                if chapter_name is not None:
                    book_current_chapter_name = chapter_name.find("span", attrs={"class": "content-wrap"}).string

                    f.write(book_current_chapter_name + "\n")
                    all_line = book_read_soup.select(".read-content p")
                    for line in all_line:
                        paragraph = line.get_text()
                        paragraph = paragraph.replace("　　", "\n")
                        f.write("   " + paragraph + "\n")
                        break
                    chapter_next = "https:" + book_read_soup.find("a", attrs={"id": "j_chapterNext"}).get("href")
                    # print(chapter_next)
                    book_read_soup = BeautifulSoup(requests.get(chapter_next).text, "html.parser")
                    print("《" + book_current_chapter_name + "》已存储到本地")
                else:
                    break
        f.close()

        # Save the data to database ================================
        sql = f"""insert into python_book(book_img,book_title,book_author,book_type,book_state,
                book_latest_chapter,book_latest_chapter_time,book_content,book_detail_url,book_store_free_path) \
                VALUES ('{book_img_url}','{book_title}','{book_author}','{book_type}','{book_state}',
                '{book_latest_chapter}','{book_latest_time}','{book_content}','{book_detail_url}','{book_store_path_mysql}')"""
        try:
            #  print(sql)
            cursor.execute(sql)
            database.commit()
            print("小说《" + book_title + "》已存储到存储到数据库==================================================")
            book_store_free_path = ""
        except Exception as e:
            print(e)
            database.rollback()

database.close()
