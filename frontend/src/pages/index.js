// src/pages/index.js

import MusicChartsDashboard from '../components/MusicChartsDashboard';

export default function Home({ appleMusicData, youtubeMusicData, spotifyData }) {
  return (
    <MusicChartsDashboard 
      appleMusicData={appleMusicData} 
      youtubeMusicData={youtubeMusicData} 
      spotifyData={spotifyData} 
    />
  );
}

export async function getServerSideProps() {
  const resApple = await fetch('http://localhost:5000/api/apple-music');
  const appleMusicData = await resApple.json();

  const resYoutube = await fetch('http://localhost:5000/api/youtube');
  const youtubeMusicData = await resYoutube.json();

  const resSpotify = await fetch('http://localhost:5000/api/spotify');
  const spotifyData = await resSpotify.json();

  return {
    props: {
      appleMusicData,
      youtubeMusicData,
      spotifyData,
    },
  };
}
