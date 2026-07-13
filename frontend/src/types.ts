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

export type ErrorResponse = {
  detail: string;
};

export type Release = {
  id: string;
  name: string;
  artist: string;
  url: string | null;
  notified_at: string;
};

export type ReleasesResponse = {
  status: string;
  releases: Release[];
};
