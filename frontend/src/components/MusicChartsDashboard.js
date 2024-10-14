import React, { useState } from 'react';
import Image from "next/image";
import Link from "next/link";
import { Music } from "lucide-react"; // 필요에 따라 추가 라이브러리 가져오기

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs";

export function MusicChartsDashboard({ appleMusicData, youtubeMusicData, spotifyData }) {
  const [activeTab, setActiveTab] = useState("apple");

  return (
    <div className="flex min-h-screen w-full flex-col bg-background text-foreground">
      <aside className="fixed inset-y-0 left-0 z-10 hidden w-14 flex-col border-r bg-muted/40 sm:flex">
        <nav className="flex flex-col items-center gap-4 px-2 sm:py-5">
          <Link
            href="#"
            className="group flex h-9 w-9 shrink-0 items-center justify-center gap-2 rounded-full bg-primary text-lg font-semibold text-primary-foreground md:h-8 md:w-8 md:text-base"
          >
            <Music className="h-4 w-4 transition-all group-hover:scale-110" />
            <span className="sr-only">Music Charts</span>
          </Link>
        </nav>
      </aside>
      <div className="flex flex-col sm:gap-4 sm:py-4 sm:pl-14">
        <header className="sticky top-0 z-30 flex h-14 items-center gap-4 border-b bg-background px-4 sm:static sm:h-auto sm:border-0 sm:bg-transparent sm:px-6">
          <h1 className="text-2xl font-bold">Daily Rank</h1>
        </header>
        <main className="grid flex-1 items-start gap-4 p-4 sm:px-6 sm:py-0 md:gap-8">
          <Tabs defaultValue="apple" onValueChange={setActiveTab}>
            <div className="flex items-center">
              <TabsList>
                <TabsTrigger value="apple">Apple Music</TabsTrigger>
                <TabsTrigger value="youtube">YouTube Music</TabsTrigger>
                <TabsTrigger value="spotify">Spotify</TabsTrigger>
              </TabsList>
            </div>
            <TabsContent value="apple">
              <Card>
                <CardHeader>
                  <CardTitle>Apple Music Charts</CardTitle>
                  <CardDescription>
                    Top tracks on Apple Music
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead className="w-[100px]">Rank</TableHead>
                        <TableHead>Thumbnail</TableHead>
                        <TableHead>Title</TableHead>
                        <TableHead>Artist</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {appleMusicData.map((track, index) => (
                        <TableRow key={track.id || index}>
                          <TableCell>{index + 1}</TableCell>
                          <TableCell>
                            <Image
                              src={track.thumbnail_link}
                              alt={`${track.title} thumbnail`}
                              width={50}
                              height={50}
                              className="rounded-md"
                            />
                          </TableCell>
                          <TableCell>
                            <Link href={track.link} target="_blank" className="hover:underline">
                              {track.title}
                            </Link>
                          </TableCell>
                          <TableCell>
                            <Link href={track.artist_link} target="_blank" className="hover:underline">
                              {track.artist}
                            </Link>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </CardContent>
              </Card>
            </TabsContent>
            <TabsContent value="youtube">
              <Card>
                <CardHeader>
                  <CardTitle>YouTube Music Charts</CardTitle>
                  <CardDescription>
                    Top tracks on YouTube Music
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead className="w-[100px]">Rank</TableHead>
                        <TableHead>Thumbnail</TableHead>
                        <TableHead>Title</TableHead>
                        <TableHead>Artist</TableHead>
                        <TableHead>Views</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {youtubeMusicData.map((track) => (
                        <TableRow key={track.id}>
                          <TableCell>{track.current_position}</TableCell>
                          <TableCell>
                            <Image
                              src={track.thumbnail_link}
                              alt={`${track.title} thumbnail`}
                              width={50}
                              height={50}
                              className="rounded-md"
                            />
                          </TableCell>
                          <TableCell>
                            <Link href={track.song_link} target="_blank" className="hover:underline">
                              {track.title}
                            </Link>
                          </TableCell>
                          <TableCell>
                            <Link href={track.artist_link} target="_blank" className="hover:underline">
                              {track.artist}
                            </Link>
                          </TableCell>
                          <TableCell>{track.views}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </CardContent>
              </Card>
            </TabsContent>
            <TabsContent value="spotify">
              <Card>
                <CardHeader>
                  <CardTitle>Spotify Charts</CardTitle>
                  <CardDescription>
                    Top tracks on Spotify
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead className="w-[100px]">Rank</TableHead>
                        <TableHead>Thumbnail</TableHead>
                        <TableHead>Title</TableHead>
                        <TableHead>Artist</TableHead>
                        <TableHead>Streams</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {spotifyData.map((track) => (
                        <TableRow key={track.id}>
                          <TableCell>{track.current_position}</TableCell>
                          <TableCell>
                            <Image
                              src={track.thumbnail_link}
                              alt={`${track.title} thumbnail`}
                              width={50}
                              height={50}
                              className="rounded-md"
                            />
                          </TableCell>
                          <TableCell>
                            <Link href={track.song_link} target="_blank" className="hover:underline">
                              {track.title}
                            </Link>
                          </TableCell>
                          <TableCell>
                            <Link href={track.artist_link} target="_blank" className="hover:underline">
                              {track.artist}
                            </Link>
                          </TableCell>
                          <TableCell>{track.streams}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </main>
      </div>
    </div>
  );
}

export default MusicChartsDashboard;
