from bs4 import BeautifulSoup

def parse_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    articles = soup.find_all('article')

    result = []
    for article in articles:
        # Judul & Link
        title_tag = article.find('h2', class_='font-weight-semibold')
        title = title_tag.get_text(strip=True) if title_tag else ''
        link = title_tag.find('a')['href'] if title_tag and title_tag.find('a') else ''

        # Ringkasan
        summary_tag = article.find('p', class_='text-justify')
        summary = summary_tag.get_text(strip=True) if summary_tag else ''

        # View Count
        views = '0 View'
        post_meta = article.find('div', class_='post-meta')
        if post_meta:
            spans = post_meta.find_all('span')
            for span in spans:
                icon = span.find('i', class_='far fa-eye')
                if icon:
                    a_tag = span.find('a')
                    if a_tag:
                        views = a_tag.get_text(strip=True)
                    break

        # Tanggal
        day = article.find('span', class_='day')
        month = article.find('span', class_='month')
        date = f"{day.text.strip()} {month.text.strip()}" if day and month else ''

        result.append({
            'judul': title,
            'tanggal': date,
            'link': link,
            'ringkasan': summary,
            'dilihat': views
        })

    return result
