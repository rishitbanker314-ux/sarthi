import { useState, useEffect, useRef } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, Modal, ScrollView, ActivityIndicator, KeyboardAvoidingView, Platform } from 'react-native';
import { useStreamMobile } from '@/lib/useStreamMobile';

export function TutorChat({ lessonId, onClose, token }: { lessonId: string, onClose: () => void, token: string | null }) {
  const [messages, setMessages] = useState<{ role: 'user' | 'assistant', content: string }[]>([]);
  const [input, setInput] = useState('');
  const [activeMessage, setActiveMessage] = useState('');
  const activeMessageRef = useRef('');

  useEffect(() => {
    activeMessageRef.current = activeMessage;
  }, [activeMessage]);

  const { startStream, isStreaming } = useStreamMobile({
    url: `${process.env.EXPO_PUBLIC_API_BASE || 'http://localhost:4010/api/v1'}/tutor/messages`,
    method: 'POST',
    body: {
      lesson_id: lessonId,
      message: input,
      history: messages.map(m => ({ role: m.role, content: m.content })),
    },
    headers: token ? { Authorization: `Bearer ${token}` } : undefined,
    onEvent: (event) => {
      if (event.type === 'token') {
        setActiveMessage(prev => prev + event.text);
      }
    },
    onDone: () => {
      setMessages(prev => [...prev, { role: 'assistant', content: activeMessageRef.current }]);
      setActiveMessage('');
      activeMessageRef.current = '';
    }
  });

  // Small hack: need to update activeMessage closure in useStreamMobile.
  // Actually, onDone uses the old activeMessage state because it's not in the dependency array of startStream correctly,
  // but it's fine for this demo if we just flush activeMessage in a different way or use functional state updates.
  // Let's modify onDone slightly by using functional state update if needed.
  
  const sendMessage = () => {
    if (!input.trim() || !token || isStreaming) return;
    setMessages(prev => [...prev, { role: 'user', content: input }]);
    setActiveMessage('');
    startStream();
    setInput('');
  };

  return (
    <Modal visible animationType="slide" transparent>
      <KeyboardAvoidingView 
        style={styles.overlay} 
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      >
        <View style={styles.sheet}>
          <View style={styles.header}>
            <Text style={styles.title}>Tutor</Text>
            <TouchableOpacity onPress={onClose}>
              <Text style={styles.close}>Close</Text>
            </TouchableOpacity>
          </View>
          
          <ScrollView style={styles.chatArea}>
            {messages.map((m, i) => (
              <View key={i} style={[styles.bubble, m.role === 'user' ? styles.userBubble : styles.tutorBubble]}>
                <Text style={[styles.text, m.role === 'user' ? styles.userText : styles.tutorText]}>
                  {m.content}
                </Text>
              </View>
            ))}
            {isStreaming && (
              <View style={[styles.bubble, styles.tutorBubble]}>
                <Text style={styles.tutorText}>{activeMessage}</Text>
                {!activeMessage && <ActivityIndicator size="small" />}
              </View>
            )}
          </ScrollView>

          <View style={styles.inputArea}>
            <TextInput
              style={styles.input}
              value={input}
              onChangeText={setInput}
              placeholder="Ask a question..."
              multiline
            />
            <TouchableOpacity style={styles.sendButton} onPress={sendMessage}>
              <Text style={styles.sendText}>Send</Text>
            </TouchableOpacity>
          </View>
        </View>
      </KeyboardAvoidingView>
    </Modal>
  );
}

const styles = StyleSheet.create({
  overlay: { flex: 1, justifyContent: 'flex-end', backgroundColor: 'rgba(0,0,0,0.5)' },
  sheet: { height: '80%', backgroundColor: '#fff', borderTopLeftRadius: 20, borderTopRightRadius: 20, padding: 16 },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingBottom: 16, borderBottomWidth: 1, borderBottomColor: '#eee' },
  title: { fontSize: 18, fontWeight: 'bold' },
  close: { fontSize: 16, color: '#007AFF' },
  chatArea: { flex: 1, marginVertical: 16 },
  bubble: { padding: 12, borderRadius: 12, marginBottom: 8, maxWidth: '80%' },
  userBubble: { backgroundColor: '#007AFF', alignSelf: 'flex-end', borderBottomRightRadius: 4 },
  tutorBubble: { backgroundColor: '#f0f0f0', alignSelf: 'flex-start', borderBottomLeftRadius: 4 },
  text: { fontSize: 16 },
  userText: { color: '#fff' },
  tutorText: { color: '#000' },
  inputArea: { flexDirection: 'row', alignItems: 'flex-end', gap: 12 },
  input: { flex: 1, backgroundColor: '#f9f9f9', borderWidth: 1, borderColor: '#ddd', borderRadius: 20, paddingHorizontal: 16, paddingVertical: 12, maxHeight: 100 },
  sendButton: { padding: 12 },
  sendText: { color: '#007AFF', fontWeight: 'bold', fontSize: 16 },
});
