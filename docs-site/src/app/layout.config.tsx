import type {BaseLayoutProps} from 'fumadocs-ui/layouts/shared';
import Discord from "@/app/Discord";
import Image from "next/image";
import Link from "next/link";
import GithubInfoClient from "@/components/github-info-client";

/**
 * Shared layout configurations
 *
 * you can customise layouts individually from:
 * Home Layout: app/(home)/layout.tsx
 * Docs Layout: app/docs/layout.tsx
 */
export const baseOptions: BaseLayoutProps = {
    nav: {
        title: (
            <Link href="/" className="flex items-center">
                <Image
                    className="h-7 w-auto"
                    src={`${process.env.BASE_PATH ?? ''}/media/icon.png`}
                    alt="Maple Sim"
                    width={160}
                    height={20}
                    priority
                />
            </Link>
        ),
    },
    // see https://fumadocs.dev/docs/ui/navigation/links
    links: [
        {
            text: "Docs",
            url: `${process.env.BASE_PATH ?? ""}/docs`,
        },
        {
            type: 'custom',
            children: (
                <GithubInfoClient owner="Shenzhen-Robotics-Alliance" repo="maple-sim" className="lg:-mx-2"/>
            ),
        },
        {
            text: "Discord",
            url: "https://discord.gg/UsV8Qpwn",
            icon: <Discord />,
            type: 'icon'
        }
    ],
    // githubUrl: "https://github.com/Shenzhen-Robotics-Alliance/maple-sim"
};
