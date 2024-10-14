from flask import Flask, render_template, jsonify
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    StaleElementReferenceException,
    NoSuchElementException,
)
from logging.handlers import RotatingFileHandler
from apscheduler.schedulers.background import BackgroundScheduler
from models import db, YouTubeChart, SpotifyChart, AppleMusicChart
import os
import time
import logging
import json
import urllib.parse
from flask_cors import CORS

log_handler = RotatingFileHandler("app.log", maxBytes=10000, backupCount=1)
log_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
log_handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(log_handler)


def create_app():
    app = Flask(__name__)
    CORS(app)

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///music_data.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    # 데이터베이스 초기화
    with app.app_context():
        db.create_all()  # 데이터베이스와 테이블 생성

    return app


load_dotenv("key.env")


# Apple Music Scrape
def scrape_apple_music_chart():
    driver = webdriver.Chrome()
    driver.set_window_size(1200, 800)
    last_song_count = 0

    url = "https://music.apple.com/jp/new/top-charts/songs"
    driver.get(url)

    time.sleep(3)

    apple_music_data = []
    scroll_pause_time = 2

    scrollable_element = driver.find_element(By.ID, "scrollable-page")

    while len(apple_music_data) < 100:
        for _ in range(5):
            driver.execute_script(
                "arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_element
            )
            time.sleep(scroll_pause_time)

        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "songs-list-row"))
            )
        except TimeoutException:
            print("타임아웃: 더 이상 새로운 요소를 찾을 수 없습니다.")
            break

        songs_container = driver.find_elements(By.CLASS_NAME, "songs-list-row")

        for song in songs_container:
            try:
                aria_label = song.get_attribute("aria-label")
                if aria_label:
                    title_artist = aria_label.split("、")
                    title = title_artist[0].strip()
                    artist = (
                        title_artist[1].strip()
                        if len(title_artist) > 1
                        else "알 수 없음"
                    )
                    source_elements = song.find_elements(By.TAG_NAME, "source")
                    thumbnail_link = None
                    if source_elements:
                        thumbnail_link = (
                            source_elements[0]
                            .get_attribute("srcset")
                            .split(",")[0]
                            .strip()
                            .split(" ")[0]
                        )
                    link_element = song.find_element(
                        By.CSS_SELECTOR, "a[data-testid='click-action']"
                    )
                    link = link_element.get_attribute("href")
                    artist_link = None
                    artist_link_elements = song.find_elements(
                        By.CSS_SELECTOR, "a[data-testid='click-action']"
                    )
                    for element in artist_link_elements:
                        href = element.get_attribute("href")
                        if (
                            "artist" in href
                        ):  # 선택자가 곡과 가수가 같기에 링크에 artist가 들어가는 요소를 찾음
                            artist_link = href
                            break

                    if artist_link is not None:
                        apple_music_data.append(
                            {
                                "title": title,
                                "artist": artist,
                                "link": link,
                                "artist_link": artist_link,
                                "thumbnail_link": thumbnail_link,
                            }
                        )
                        print(
                            f"저장된 데이터 - 제목: {title}, 아티스트: {artist}, 링크: {link}, 아티스트 링크: {artist_link}, 썸네일 링크: {thumbnail_link} (현재 {len(apple_music_data)}개)"
                        )
            except StaleElementReferenceException:
                print("요소가 오래되었습니다. 다음 요소로 넘어갑니다.")
                continue

        last_song_count = len(apple_music_data)

    print(f"총 {len(apple_music_data)}개의 곡을 수집했습니다.")
    logger.info(f"Apple Music: 총 {len(apple_music_data)}개의 곡을 수집했습니다.")
    driver.quit()
    return apple_music_data[:100]


# Spotify Scrape
def scrape_spotify_chart(username, password):
    driver = webdriver.Chrome()
    driver.set_window_size(1200, 800)

    driver.get("https://charts.spotify.com/charts/view/regional-jp-weekly/latest")
    time.sleep(2)

    # Login Required
    login_button = driver.find_element(By.XPATH, '//a[@data-testid="charts-login"]')
    login_button.click()

    time.sleep(2)
    id_input = driver.find_element(By.XPATH, '//*[@id="login-username"]')
    id_input.send_keys(username)

    password_input = driver.find_element(By.XPATH, '//*[@id="login-password"]')
    password_input.send_keys(password)

    login_button = driver.find_element(By.XPATH, '//*[@id="login-button"]')
    login_button.click()

    time.sleep(3)
    driver.get("https://charts.spotify.com/charts/view/regional-jp-weekly/latest")
    time.sleep(5)

    spotify_data = []

    try:
        songs_container = driver.find_elements(
            By.CSS_SELECTOR, "div[data-testid='charts-table'] tbody tr"
        )

        for song in songs_container:
            try:
                title_element = song.find_element(
                    By.CSS_SELECTOR, "span[class*='styled__StyledTruncatedTitle']"
                )
                title = title_element.text.strip()

                song_link_element = song.find_element(
                    By.CSS_SELECTOR, "a[href^='https://open.spotify.com/track/']"
                )
                song_link = song_link_element.get_attribute("href")

                artist_element = song.find_element(
                    By.CSS_SELECTOR, "div[class*='styled__StyledArtistsTruncated']"
                )
                artist = artist_element.text.strip()
                artist_link = artist_element.find_element(
                    By.TAG_NAME, "a"
                ).get_attribute("href")

                current_position = song.find_element(
                    By.CSS_SELECTOR, "span[aria-label='Current position']"
                ).text.strip()
                previous_rank = song.find_element(
                    By.CSS_SELECTOR, "td[class*='styled__RightTableCell'] span"
                ).text.strip()

                stream_td_elements = song.find_elements(
                    By.CSS_SELECTOR, "td[class*='styled__RightTableCell']"
                )
                streams = next(
                    (
                        td.text.strip()
                        for td in reversed(stream_td_elements)
                        if td.text.strip()
                    ),
                    None,
                )

                thumbnail_element = song.find_element(
                    By.CSS_SELECTOR, "img[class*='Image-sc-']"
                )
                thumbnail_link = thumbnail_element.get_attribute("src")

                spotify_data.append(
                    {
                        "title": title,
                        "artist": artist,
                        "current_position": current_position,
                        "previous_rank": previous_rank,
                        "streams": streams,
                        "song_link": song_link,
                        "artist_link": artist_link,
                        "thumbnail_link": thumbnail_link,
                    }
                )
                print(
                    f"저장할 데이터 - 제목: {title}, 아티스트: {artist}, 현재 순위: {current_position}, 이전 순위: {previous_rank}, "
                    f"재생 횟수: {streams}, 곡 링크: {song_link}, 아티스트 링크: {artist_link}, 썸네일 링크: {thumbnail_link}"
                )

            except StaleElementReferenceException:
                continue
            except NoSuchElementException as e:
                print(f"요소를 찾을 수 없음: {e}")
                print(f"현재 처리 중인 곡: {title}")
                print(f"HTML: {song.get_attribute('outerHTML')}")
                continue

    except Exception as e:
        print(f"오류 발생: {e}")

    print(f"총 {len(spotify_data)}개의 곡을 수집했습니다.")
    logger.info(f"Spotify: 총 {len(spotify_data)}개의 곡을 수집했습니다.")
    driver.quit()
    return spotify_data[:100]


# Shadow DOM 접근 함수
def expand_shadow_element(driver, element):
    shadow_root = driver.execute_script("return arguments[0].shadowRoot", element)
    return shadow_root


# Youtube Music Chart Scrape
def scrape_youtube_chart():
    driver = webdriver.Chrome()
    driver.set_window_size(1200, 800)

    driver.get("https://charts.youtube.com/charts/TopSongs/jp/weekly")

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "ytmc-v2-app"))
        )
        time.sleep(5)

    except TimeoutException:
        print("페이지 로딩 시간 초과")
        driver.quit()
        return []

    youtube_data = []

    try:
        # Shadow DOM에 접근하여 필요한 요소 가져오기
        shadow_host_app = driver.find_element(By.CSS_SELECTOR, "ytmc-v2-app")
        shadow_root_app = expand_shadow_element(driver, shadow_host_app)
        shadow_host_detailed_page = shadow_root_app.find_element(
            By.CSS_SELECTOR, "ytmc-detailed-page"
        )
        shadow_root_detailed_page = expand_shadow_element(
            driver, shadow_host_detailed_page
        )
        chart_table_container = shadow_root_detailed_page.find_element(
            By.CSS_SELECTOR,
            "div.ytmc-chart-table-v2-container.style-scope.ytmc-detailed-page",
        )
        shadow_host_chart_table = chart_table_container.find_element(
            By.CSS_SELECTOR, "ytmc-chart-table-v2"
        )
        shadow_root_chart_table = expand_shadow_element(driver, shadow_host_chart_table)
        song_entries = shadow_root_chart_table.find_elements(
            By.CSS_SELECTOR, "ytmc-entry-row"
        )

        if not song_entries:
            print("요소를 찾을 수 없습니다.")
            driver.quit()
            return []

        for entry in song_entries:
            try:
                rank_container = expand_shadow_element(driver, entry)
                current_position = rank_container.find_element(
                    By.CSS_SELECTOR, "span#rank"
                ).text.strip()
                title_element = rank_container.find_element(
                    By.CSS_SELECTOR, "div#entity-title"
                )
                title = title_element.text.strip()
                artist_element = rank_container.find_element(
                    By.CSS_SELECTOR, "span.artistName"
                )
                artist = artist_element.text.strip()
                release_date = rank_container.find_element(
                    By.CSS_SELECTOR, ".detailed-view-release-date"
                ).text.strip()
                previous_rank = rank_container.find_elements(
                    By.CSS_SELECTOR, ".metric.content.center"
                )[1].text.strip()
                chart_duration = rank_container.find_elements(
                    By.CSS_SELECTOR, ".tablet-non-displayed-metric"
                )[0].text.strip()
                views = rank_container.find_elements(
                    By.CSS_SELECTOR, ".tablet-non-displayed-metric"
                )[1].text.strip()
                thumbnail_element = rank_container.find_element(
                    By.CSS_SELECTOR, "img.style-scope.ytmc-entry-row"
                )
                thumbnail_link = (
                    thumbnail_element.get_attribute("src")
                    if thumbnail_element
                    else None
                )

                # 곡 링크 추출
                song_endpoint = title_element.get_attribute("endpoint")
                song_link = None
                if song_endpoint:
                    song_data = json.loads(song_endpoint)
                    song_link = song_data.get("urlEndpoint", {}).get("url")

                # 아티스트 링크 추출
                artist_endpoint = artist_element.get_attribute("endpoint")
                artist_link = None
                if artist_endpoint:
                    try:
                        artist_data = json.loads(artist_endpoint)
                        query = artist_data.get("browseEndpoint", {}).get("query", "")
                        artist_params_id = (
                            query.split(":")[-1].strip('"').rstrip("}").strip('"')
                            if ":" in query
                            else ""
                        )
                        if artist_params_id:
                            # 디코딩 후 다시 인코딩
                            decoded = urllib.parse.unquote(artist_params_id)
                            print(f"Decoded: {decoded}")
                            # '/' 문자를 수동으로 '%2F'로 변경
                            encoded = decoded.replace("/", "%2F")
                            print(f"After manual encoding: {encoded}")
                            artist_params_id = encoded
                            print(f"Final artist_params_id: {artist_params_id}")
                            artist_link = (
                                f"https://charts.youtube.com/artist/{artist_params_id}"
                            )
                            print(f"Final artist_link: {artist_link}")
                        else:
                            print(
                                f"Warning: No artistParamsId found for artist {artist}"
                            )
                    except json.JSONDecodeError:
                        print(f"Warning: Invalid JSON in artist endpoint for {artist}")
                    except Exception as e:
                        print(
                            f"Warning: Error processing artist link for {artist}: {e}"
                        )
                else:
                    print(f"Warning: No endpoint found for artist {artist}")

                # None 값을 빈 문자열로 대체
                youtube_data.append(
                    {
                        "title": title,
                        "artist": artist,
                        "current_position": current_position,
                        "release_date": release_date or "",
                        "previous_rank": previous_rank or "",
                        "chart_duration": chart_duration or "",
                        "views": views or "",
                        "song_link": song_link or "",
                        "artist_link": artist_link or "",
                        "thumbnail_link": thumbnail_link or "",
                    }
                )

                print(
                    f"저장된 데이터 - 제목: {title}, 아티스트: {artist}, 순위: {current_position}, 발매일: {release_date}, "
                    f"지난 순위: {previous_rank}, 차트 지속 기간: {chart_duration}, 조회수: {views}, "
                    f"곡 링크: {song_link}, 아티스트 링크: {artist_link}, 썸네일 링크: {thumbnail_link}"
                )

            except Exception as e:
                print(f"데이터 추출 중 오류: {e}")
                continue

    except Exception as e:
        print(f"오류 발생: {e}")

    print(f"총 {len(youtube_data)}개의 곡을 수집했습니다.")
    logger.info(f"YouTube Music: 총 {len(youtube_data)}개의 곡을 수집했습니다.")
    driver.quit()
    return youtube_data[:100]


app = create_app()


def scrape_and_store_data():
    logger.info("데이터 스크래핑 시작")

    # spotify_username = os.getenv('SPOTIFY_USERNAME')
    # spotify_password = os.getenv('SPOTIFY_PASSWORD')

    apple_music_data = scrape_apple_music_chart()
    youtube_data = scrape_youtube_chart()
    spotify_data = scrape_spotify_chart(
        os.getenv("SPOTIFY_USERNAME"), os.getenv("SPOTIFY_PASSWORD")
    )

    with app.app_context():
        # 데이터베이스에 저장

        YouTubeChart.query.delete()

        for song in youtube_data:
            new_song = YouTubeChart(
                title=song["title"],
                artist=song["artist"],
                current_position=song["current_position"],
                previous_rank=song["previous_rank"],
                views=song["views"],
                song_link=song["song_link"],
                artist_link=song["artist_link"],
                thumbnail_link=song["thumbnail_link"],
            )
            db.session.add(new_song)
        db.session.commit()

        logger.info(f"YouTube 차트 데이터 저장됨: {len(youtube_data)}개")

        SpotifyChart.query.delete()

        for song in spotify_data:
            new_song = SpotifyChart(
                title=song["title"],
                artist=song["artist"],
                current_position=song["current_position"],
                previous_rank=song["previous_rank"],
                streams=song["streams"],
                song_link=song["song_link"],
                artist_link=song["artist_link"],
                thumbnail_link=song["thumbnail_link"],
            )
            db.session.add(new_song)
        db.session.commit()

        logger.info(f"Spotify 차트 데이터 저장됨: {len(spotify_data)}개")

        AppleMusicChart.query.delete()

        for song in apple_music_data:
            new_song = AppleMusicChart(
                title=song["title"],
                artist=song["artist"],
                link=song["link"],
                artist_link=song["artist_link"],
                thumbnail_link=song["thumbnail_link"],
            )
            db.session.add(new_song)
        db.session.commit()

        logger.info(
            f"Apple Music 차트 데이터 저장됨: {AppleMusicChart.query.count()}개"
        )

    logger.info("데이터 스크래핑 종료")


scheduler = BackgroundScheduler(timezone="Asia/Seoul")
scheduler.add_job(
    scrape_and_store_data, "cron", hour="0,12", misfire_grace_time=300
)  # 매일 0시와 12시에 실행, 지연 시 5분 이내에 실행
scheduler.start()


@app.route("/")
def index():
    logger.info("index() 함수 호출됨")

    youtube_data = YouTubeChart.query.limit(100).all()
    spotify_data = SpotifyChart.query.limit(100).all()
    apple_music_data = AppleMusicChart.query.limit(100).all()

    logger.info(f"Apple Music 데이터 개수: {len(apple_music_data)}")

    return render_template(
        "index.html",
        youtube=youtube_data,
        spotify=spotify_data,
        apple_music=apple_music_data,
    )


@app.route("/api/music-charts", methods=["GET"])
def get_music_charts():
    with app.app_context():
        youtube_data = YouTubeChart.query.limit(100).all()
        spotify_data = SpotifyChart.query.limit(100).all()
        apple_music_data = AppleMusicChart.query.limit(100).all()

        return jsonify(
            {
                "youtube": [track.to_dict() for track in youtube_data],
                "spotify": [track.to_dict() for track in spotify_data],
                "apple_music": [track.to_dict() for track in apple_music_data],
            }
        )


@app.route("/api/apple-music", methods=["GET"])
def get_apple_music_data():
    with app.app_context():
        apple_music_data = AppleMusicChart.query.all()
        return jsonify([song.to_dict() for song in apple_music_data])


@app.route("/api/youtube", methods=["GET"])
def get_youtube_data():
    with app.app_context():
        youtube_data = YouTubeChart.query.all()
        return jsonify([song.to_dict() for song in youtube_data])


@app.route("/api/spotify", methods=["GET"])
def get_spotify_data():
    with app.app_context():
        spotify_data = SpotifyChart.query.all()
        return jsonify([song.to_dict() for song in spotify_data])


@app.errorhandler(404)
def page_not_found(e):
    logger.error(f"404 에러 발생: {str(e)}")
    return jsonify({"error": "페이지를 찾을 수 없습니다."}), 404


@app.errorhandler(500)
def internal_server_error(e):
    logger.error(f"500 에러 발생: {str(e)}")
    return jsonify({"error": "서버 내부 오류가 발생했습니다."}), 500


if __name__ == "__main__":
    app.run(debug=True)
