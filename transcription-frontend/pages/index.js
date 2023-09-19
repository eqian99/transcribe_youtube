import { useState } from 'react';

export default function Home() {
  const [isLoading, setIsLoading] = useState(false);
  const [isChat, setIsChat] = useState(false);
  const [userInput, setUserInput] = useState("");
  const [chatHistory, setChatHistory] = useState([]);

  const handleAudioSubmit = async (e) => {
    if (e.key === 'Enter') {
      setIsLoading(true);
      try {
        const response = await fetch("http://localhost:8080/parse_audio", {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({ youtube_url: userInput })
        });
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        // Don't display the returned text, instead display "Audio processed"
        setChatHistory([{ speaker: 'System', content: 'Audio processed' }]);
        setIsChat(true);
        // Clear the userInput after processing the audio
        setUserInput("");
      } catch (error) {
        console.error('An error occurred:', error);
      } finally {
        setIsLoading(false);
      }
    }
  };

  const handleChatSubmit = async (e) => {
    if (e.key === 'Enter') {
      setIsLoading(true);
      try {
        const response = await fetch("http://localhost:8080/chat", {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({ user_input: userInput })
        });
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setChatHistory([...chatHistory, { speaker: 'Human', content: userInput }, { speaker: 'Assistant', content: data.output }]);
        // Clear the userInput after submitting the chat
        setUserInput("");
      } catch (error) {
        console.error('An error occurred:', error);
      } finally {
        setIsLoading(false);
      }
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 py-2">
      <div className="max-w-md w-full space-y-8 text-center">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            {isChat ? 'Chat' : 'Transcribe YouTube Audio'}
          </h2>
        </div>
        {isChat ? (
          <div className="rounded-md shadow-md bg-white p-6">
            <div className="border p-4 h-60 overflow-y-auto">
              {chatHistory.map((msg, index) => (
                <div key={index} className="font-medium text-gray-700">{msg.speaker}: {msg.content}</div>
              ))}
            </div>
            <input
              className="mt-4 w-full p-2 border border-gray-300 rounded-md"
              type="text"
              value={userInput}
              onChange={(e) => setUserInput(e.target.value)}
              onKeyPress={handleChatSubmit}
              placeholder="Type your message here..."
            />
          </div>
        ) : (
          <input
            className="w-full p-2 border border-gray-300 rounded-md"
            type="text"
            placeholder="Enter YouTube URL"
            onChange={(e) => setUserInput(e.target.value)}
            onKeyPress={handleAudioSubmit}
          />
        )}
        {isLoading && <div className="mt-4 text-blue-500">Loading...</div>}
      </div>
    </div>
  );
}