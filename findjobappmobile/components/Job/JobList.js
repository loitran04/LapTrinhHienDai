import { useEffect, useState } from "react";
import { FlatList, View, Text, Alert } from "react-native";
import { Card, Button } from "react-native-paper";
import { useNavigation } from "@react-navigation/native";
import AsyncStorage from "@react-native-async-storage/async-storage";
import API, { authApis, endpoints } from "../../configs/API";
import MyStyles from "../../styles/MyStyles";
import { SafeAreaView } from "react-native-safe-area-context";

const JobList = () => {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const nav = useNavigation();

  const loadJobs = async () => {
    try {
      const token = await AsyncStorage.getItem("access_token");
      const empRes = await authApis(token).get(endpoints["current-employer"]);
      const employerId = empRes.data.id;
      const jobRes = await authApis(token).get(endpoints["jobs"]);
      const filtered = jobRes.data.filter(j => j.employer_id === employerId);
      setJobs(filtered);
    } catch (err) {
      Alert.alert("Lỗi", "Không thể tải danh sách công việc.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadJobs();
  }, []);

  const renderItem = ({ item }) => (
    <SafeAreaView style={{ flex: 1 }}>
      <Card style={MyStyles.mar}>
        <Card.Title title={item.title} />
        <Card.Content>
          <Text>📍 {item.location}</Text>
        </Card.Content>
        <Card.Actions>
          <Button onPress={() => nav.navigate("Applicants", { jobId: item.id })}>
            Xem ứng viên
          </Button>
        </Card.Actions>
      </Card>
    </SafeAreaView>
  );

  return loading ? (
    <Text style={{ textAlign: "center", marginTop: 20 }}>Đang tải danh sách...</Text>
  ) : jobs.length === 0 ? (
    <Text style={{ textAlign: "center", marginTop: 20 }}>Không có job nào do bạn đăng.</Text>
  ) : (
    <FlatList data={jobs} renderItem={renderItem} keyExtractor={j => j.id.toString()} />
  );
};

export default JobList;
