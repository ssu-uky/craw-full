import React, { useEffect, useState } from 'react';
import MusicChartsDashboard from '../components/MusicChartsDashboard'; // 경로 조정 필요

const MusicChartsPage = () => {
  const [appleMusicData, setAppleMusicData] = useState([]);
  const [youtubeMusicData, setYoutubeMusicData] = useState([]);
  const [spotifyData, setSpotifyData] = useState([]);

  useEffect(() => {
    const fetchMusicCharts = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/music-charts');
        const data = await response.json();
        setAppleMusicData(data.apple);
        setYoutubeMusicData(data.youtube);
        setSpotifyData(data.spotify);
      } catch (error) {
        console.error('Error fetching music charts:', error);
      }
    };

    fetchMusicCharts();
  }, []);

  return (
    <MusicChartsDashboard 
      appleMusicData={appleMusicData}
      youtubeMusicData={youtubeMusicData}
      spotifyData={spotifyData}
    />
  );
};

export default MusicChartsPage;
