import React from 'react';
import Markdown from 'react-markdown';
import Image from 'next/image';
import Link from 'next/link';
import fs from 'fs';
import path from 'path';


export default async function HomePage() {
  
  const readmePath = path.join(process.cwd(), 'README.md');
  const readmeContent = fs.readFileSync(readmePath, 'utf-8');

  const splitContent = readmeContent.split('---');

  const overview = splitContent[1];
  const logs = splitContent.slice(2, splitContent.length - 2).filter((item) => item.trim() !== '');


  return (
    <div className="bg-gray-50 min-h-screen flex flex-col">
        {/* Header Section */}
        <header className="bg-white shadow-md">
            <div className="container mx-auto px-6 py-4 flex items-center justify-between">
                {/* Logo */}
                <Link href="/" className="flex items-center">
                    <Image src="/window.svg" alt="Logo" width={40} height={40} className="mr-3" />
                    <span className="text-xl font-bold text-gray-800">Advanced Computation & AI</span>
                </Link>

                {/* Navigation Links */}
                <nav>
                    <ul className="flex space-x-6">
                        <li><Link href="#" className="text-blue-600 hover:text-blue-800 transition duration-300">Overview</Link></li>
                        <li><Link href="#" className="text-blue-600 hover:text-blue-800 transition duration-300">Research Log</Link></li>
                        <li><Link href="#" className="text-blue-600 hover:text-blue-800 transition duration-300">Frameworks</Link></li>
                        <li><Link href="#" className="text-blue-600 hover:text-blue-800 transition duration-300">Documentation</Link></li>
                    </ul>
                </nav>
            </div>
        </header>

        {/* Main Content */}
        <main className="container mx-auto px-6 py-8 flex-grow">
            {/* Introduction Section */}
            <section className="mb-16">
                <div className="relative">
                    {/* Background Image */}
                    <Image
                        src="/globe.svg"
                        alt="Abstract Globe"
                        className="absolute top-0 left-0 w-full h-full object-cover opacity-10 z-0"
                        width={800}
                        height={600}
                    />
                    {/* Introduction Text */}
                    <div className="relative z-10 text-center">
                        <h1 className="text-5xl md:text-6xl font-bold text-gray-800 mb-6">
                            Exploring the Frontiers of Intelligence
                        </h1>
                        <p className="text-lg text-gray-600 max-w-3xl mx-auto">
                            Welcome to our research facility, a dedicated space for the exploration of advanced computation and artificial intelligence. Here, we delve into the core questions of intelligence, consciousness, and the ethical implications of our creations.
                        </p>
                    </div>
                </div>
            </section>
            {/* Diagram */}
            <section className="mb-16">
                <h2 className="text-3xl font-bold text-gray-800 mb-6">Project Architecture</h2>
                <div className="relative">
                    <Image src="/Strutcure.svg" alt="Project Structure" width={800} height={600} className="mx-auto" />
                </div>
            </section>
            
            {/* Overview Section */}
            <section className="mb-16">
                <div className="prose prose-lg max-w-full">
                    <Markdown>
                        {`# Overview of the Project`}
                    </Markdown>
                    <Markdown>
                        {overview}
                    </Markdown>
                </div>
            </section>

            {/* Research Journal Section */}
            <section className="mb-16">
                <h2 className="text-3xl font-bold text-gray-800 mb-6">Research Journal: Key Milestones</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                    {logs.map((log, index) => {
                        const logLines = log.trim().split('\n');
                        const title = logLines[0].replace('###', '').trim();
                        const dateMatch = logLines.find(line => line.startsWith('— Research Log'));
                        const date = dateMatch ? dateMatch.split(',')[1].trim() : 'Unknown Date';
                        const content = logLines.slice(1).join('\n').trim();
                        return (
                            <article key={index} className="bg-white p-6 rounded-lg shadow-md hover:shadow-xl transition-shadow duration-300">
                                <h3 className="text-xl font-semibold mb-2">{title}</h3>
                                <p className="text-sm text-gray-500 mb-4">{date}</p>
                                <div className="prose max-w-full">
                                    <Markdown>{content}</Markdown>
                                </div>
                            </article>
                        );
                    })}
                </div>
            </section>
        </main>

        {/* Footer Section */}
        <footer className="bg-gray-200 p-4 text-center text-gray-500">
            <div className="container mx-auto">
                <p>
                    © {new Date().getFullYear()} Advanced Computation & AI Research Journal
                </p>
            </div>
        </footer>
    </div>
);
}
