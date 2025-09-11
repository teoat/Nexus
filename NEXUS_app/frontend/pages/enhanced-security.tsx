import React from 'react';
import Head from 'next/head';
import dynamic from 'next/dynamic';

// Dynamically import the Enhanced Security Dashboard to avoid SSR issues
const EnhancedSecurityDashboard = dynamic(
  () => import('../src/components/EnhancedSecurityDashboard'),
  { ssr: false }
);

export default function EnhancedSecurityPage() {
  return (
    <>
      <Head>
        <title>Enhanced Security Dashboard - Nexus Platform</title>
        <meta name="description" content="Comprehensive security management with compliance monitoring, data encryption, network security, identity management, and session management" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <EnhancedSecurityDashboard />
    </>
  );
}
