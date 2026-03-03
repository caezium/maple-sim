'use client';

import { GithubInfo } from 'fumadocs-ui/components/github-info';

type GithubInfoClientProps = {
  owner: string;
  repo: string;
  className?: string;
};

export default function GithubInfoClient(props: GithubInfoClientProps) {
  return <GithubInfo {...props} />;
}
