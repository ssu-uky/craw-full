from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class YouTubeChart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    artist = db.Column(db.String, nullable=False)
    current_position = db.Column(db.String, nullable=False)
    previous_rank = db.Column(db.String, nullable=False)
    views = db.Column(db.String, nullable=False)
    song_link = db.Column(db.String, nullable=False)
    artist_link = db.Column(db.String, nullable=False)
    thumbnail_link = db.Column(db.String, nullable=False)


def to_dict(self):
    return {
        "id": self.id,
        "title": self.title,
        "artist": self.artist,
        "current_position": self.current_position,
        "previous_rank": self.previous_rank,
        "views": self.views,
        "song_link": self.song_link,
        "artist_link": self.artist_link,
        "thumbnail_link": self.thumbnail_link,
    }


class SpotifyChart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    artist = db.Column(db.String, nullable=False)
    current_position = db.Column(db.String, nullable=False)
    previous_rank = db.Column(db.String, nullable=False)
    streams = db.Column(db.String, nullable=False)
    song_link = db.Column(db.String, nullable=False)
    artist_link = db.Column(db.String, nullable=False)
    thumbnail_link = db.Column(db.String, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "artist": self.artist,
            "current_position": self.current_position,
            "previous_rank": self.previous_rank,
            "streams": self.streams,
            "song_link": self.song_link,
            "artist_link": self.artist_link,
            "thumbnail_link": self.thumbnail_link,
        }


class AppleMusicChart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    artist = db.Column(db.String, nullable=False)
    link = db.Column(db.String, nullable=False)
    artist_link = db.Column(db.String, nullable=False)
    thumbnail_link = db.Column(db.String, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "artist": self.artist,
            "link": self.link,
            "artist_link": self.artist_link,
            "thumbnail_link": self.thumbnail_link,
        }
