import { View, Text, StyleSheet, TouchableOpacity, ScrollView, ActivityIndicator } from 'react-native';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@sarathi/api-client';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';

export default function HomeScreen() {
  const router = useRouter();

  const { data: goalsResponse, isLoading: loadingGoals } = useQuery({
    queryKey: ['goals'],
    queryFn: () => apiClient.GET('/api/v1/goals', { params: { query: { page: 1, size: 1 } } }).then(res => res.data),
  });

  const planId = goalsResponse?.data?.[0]?.id;

  const { data: plan, isLoading: loadingPlan } = useQuery({
    queryKey: ['plan', planId],
    queryFn: () => apiClient.GET('/api/v1/plans/{plan_id}', { params: { path: { plan_id: planId as string } } }).then(res => res.data),
    enabled: !!planId,
  });

  if (loadingGoals || loadingPlan) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" />
      </View>
    );
  }

  const activeLesson = plan?.modules?.[0]; // Defaulting to first module

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scroll}>
        <Text style={styles.header}>Welcome back</Text>

        {activeLesson ? (
          <TouchableOpacity 
            style={styles.card}
            onPress={() => router.push(`/lesson/${activeLesson.id}`)}
          >
            <Text style={styles.cardSubtitle}>Continue Lesson</Text>
            <Text style={styles.cardTitle}>{activeLesson.title || 'In Progress'}</Text>
          </TouchableOpacity>
        ) : (
          <View style={styles.card}>
            <Text style={styles.cardTitle}>No active lesson</Text>
          </View>
        )}

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Plan Progress</Text>
          {plan ? (
            <View style={styles.planCard}>
              <Text style={styles.planTitle}>{plan.title}</Text>
              <Text style={styles.planText}>{plan.modules?.length || 0} modules</Text>
            </View>
          ) : (
            <Text>No plan active</Text>
          )}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f9f9f9' },
  scroll: { padding: 20, gap: 24 },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  header: { fontSize: 24, fontWeight: 'bold' },
  card: { backgroundColor: '#000', padding: 24, borderRadius: 12, gap: 8 },
  cardSubtitle: { color: '#ccc', fontSize: 14, textTransform: 'uppercase' },
  cardTitle: { color: '#fff', fontSize: 20, fontWeight: 'bold' },
  section: { gap: 12 },
  sectionTitle: { fontSize: 18, fontWeight: '600' },
  planCard: { backgroundColor: '#fff', padding: 16, borderRadius: 12, borderWidth: 1, borderColor: '#eee' },
  planTitle: { fontSize: 16, fontWeight: 'bold' },
  planText: { color: '#666', marginTop: 4 },
});
