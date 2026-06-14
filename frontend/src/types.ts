export type Artist = {
  id: string;
  name: string;
};

export type ArtistsResponse = {
  status: string;
  artists: Artist[];
};

export type MessageResponse = {
  status: string;
  message: string;
};
