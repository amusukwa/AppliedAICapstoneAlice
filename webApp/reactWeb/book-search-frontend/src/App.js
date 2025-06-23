import React, { useState, useRef, useEffect } from 'react';
import { 
  Container, 
  Paper, 
  TextField, 
  Button, 
  Typography, 
  Box,
  IconButton,
  ThemeProvider,
  createTheme,
  styled,
  CircularProgress,
  Fade,
  Switch,
} from '@mui/material';
import { 
  Send as SendIcon, 
  Mic as MicIcon,
  MicOff as MicOffIcon,
  Book as BookIcon,
  DarkMode as DarkModeIcon,
  LightMode as LightModeIcon,
} from '@mui/icons-material';
import { lightTheme, darkTheme } from './themes';
import axios from 'axios';

const API_URL = 'http://localhost:5000';

// Styled components
const StyledContainer = styled(Container)(({ theme }) => ({
  height: '100vh',
  padding: theme.spacing(3),
  display: 'flex',
  flexDirection: 'column',
}));

const MainPaper = styled(Paper)(({ theme }) => ({
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  borderRadius: theme.spacing(2),
  overflow: 'hidden',
  boxShadow: '0 8px 32px rgba(0,0,0,0.1)',
}));

const Header = styled(Box)(({ theme }) => ({
  padding: theme.spacing(3),
  background: theme.palette.gradient.primary,
  color: theme.palette.primary.contrastText,
  display: 'flex',
  alignItems: 'center',
  gap: theme.spacing(2),
  position: 'relative',
}));

const ChatContainer = styled(Box)(({ theme }) => ({
  flex: 1,
  overflow: 'auto',
  padding: theme.spacing(3),
  display: 'flex',
  flexDirection: 'column',
  gap: theme.spacing(2),
  backgroundColor: theme.palette.background.default,
}));

const Message = styled(Paper)(({ theme, type }) => ({
  padding: theme.spacing(2),
  maxWidth: '80%',
  borderRadius: type === 'user' ? '20px 20px 4px 20px' : '20px 20px 20px 4px',
  alignSelf: type === 'user' ? 'flex-end' : 'flex-start',
  background: type === 'user' 
    ? theme.palette.gradient.primary
    : type === 'error'
    ? theme.palette.error.light
    : theme.palette.background.paper,
  color: type === 'user' ? theme.palette.primary.contrastText : theme.palette.text.primary,
}));

const InputContainer = styled(Box)(({ theme }) => ({
  padding: theme.spacing(2),
  borderTop: `1px solid ${theme.palette.divider}`,
  display: 'flex',
  gap: theme.spacing(1),
  backgroundColor: theme.palette.background.paper,
}));

const ThemeToggle = styled(Box)(({ theme }) => ({
  position: 'absolute',
  right: theme.spacing(2),
  display: 'flex',
  alignItems: 'center',
  gap: theme.spacing(1),
}));

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(false);
  const mediaRecorder = useRef(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
      setIsDarkMode(savedTheme === 'dark');
    }
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleThemeChange = () => {
    setIsDarkMode(!isDarkMode);
    localStorage.setItem('theme', !isDarkMode ? 'dark' : 'light');
  };

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = input.trim();
    setMessages(prev => [...prev, { type: 'user', content: userMessage }]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await axios.post(`${API_URL}/query`, {
        message: userMessage
      });

      if (response.data.responses) {
        response.data.responses.forEach(resp => {
          setMessages(prev => [...prev, { 
            type: 'assistant', 
            content: resp.content 
          }]);
        });
      }
    } catch (error) {
      setMessages(prev => [...prev, { 
        type: 'error', 
        content: 'Error: Could not connect to server' 
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorder.current = new MediaRecorder(stream);
      const audioChunks = [];

      mediaRecorder.current.ondataavailable = (event) => {
        audioChunks.push(event.data);
      };

      mediaRecorder.current.onstop = async () => {
        const audioBlob = new Blob(audioChunks);
        const formData = new FormData();
        formData.append('file', audioBlob, 'voice-input.wav');

        try {
          const response = await axios.post(`${API_URL}/voice`, formData);
          if (response.data.text) {
            setInput(response.data.text);
          }
        } catch (error) {
          setMessages(prev => [...prev, { 
            type: 'error', 
            content: 'Error processing voice input' 
          }]);
        }
      };

      mediaRecorder.current.start();
      setIsRecording(true);

      // Stop recording after 5 seconds
      setTimeout(() => {
        stopRecording();
      }, 5000);

    } catch (error) {
      console.error('Error accessing microphone:', error);
    }
  };

  const stopRecording = () => {
    if (mediaRecorder.current && mediaRecorder.current.state === 'recording') {
      mediaRecorder.current.stop();
      setIsRecording(false);
    }
  };

  return (
    <ThemeProvider theme={isDarkMode ? darkTheme : lightTheme}>
      <Box sx={{ minHeight: '100vh', bgcolor: 'background.default' }}>
        <StyledContainer maxWidth="md">
          <MainPaper elevation={3}>
            <Header>
              <BookIcon fontSize="large" />
              <Typography variant="h4" component="h1">
                Book Search Assistant
              </Typography>
              <ThemeToggle>
                <LightModeIcon />
                <Switch
                  checked={isDarkMode}
                  onChange={handleThemeChange}
                  color="default"
                />
                <DarkModeIcon />
              </ThemeToggle>
            </Header>

            <ChatContainer>
              {messages.map((message, index) => (
                <Fade in={true} key={index}>
                  <Message type={message.type}>
                    <Typography>{message.content}</Typography>
                  </Message>
                </Fade>
              ))}
              {isLoading && (
                <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
                  <CircularProgress size={24} />
                </Box>
              )}
              <div ref={messagesEndRef} />
            </ChatContainer>

            <InputContainer>
              <IconButton
                color={isRecording ? "error" : "primary"}
                onClick={isRecording ? stopRecording : startRecording}
              >
                {isRecording ? <MicOffIcon /> : <MicIcon />}
              </IconButton>
              
              <TextField
                fullWidth
                variant="outlined"
                placeholder="Type your message..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSend()}
              />
              
              <Button
                variant="contained"
                endIcon={<SendIcon />}
                onClick={handleSend}
                disabled={!input.trim()}
              >
                Send
              </Button>
            </InputContainer>
          </MainPaper>
        </StyledContainer>
      </Box>
    </ThemeProvider>
  );
}

export default App;