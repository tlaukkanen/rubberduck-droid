"use client";

import {AiChat} from '@nlux/react';
import {useChatAdapter} from '@nlux/langchain-react';
import '@nlux/themes/nova.css';

const Page = () => {
  // LangServe adapter that connects to a demo LangChain Runnable API
  const adapter = useChatAdapter({
    url: '/droid'
  });

  return (
    <AiChat
      adapter={adapter}
      personaOptions={{
        assistant: {
          name: 'Droid-AI',
          avatar: 'https://docs.nlkit.com/nlux/images/personas/feather.png',
          tagline: 'Your loyal astromech companion, ready to assist!'
        },
        user: {
          name: 'Alex',
          avatar: 'https://docs.nlkit.com/nlux/images/personas/alex.png'
        }
      }}
    />
  );
};

export default Page;