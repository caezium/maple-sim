import './global.css';
import type {ReactNode} from 'react';
import {Provider} from "@/app/provider";

const basePath = process.env.BASE_PATH ?? '';

export const metadata = {
    icons: {
        icon: `${basePath}/favicon.png`,
        shortcut: `${basePath}/favicon.ico`,
        apple: `${basePath}/favicon.png`,
    },
};

export default function Layout({children}: { children: ReactNode }) {
    return (
        <html lang="en" suppressHydrationWarning>
        <body className="flex min-h-screen flex-col font-sans">
            <Provider>{children}</Provider>
        </body>
        </html>
    );
}
