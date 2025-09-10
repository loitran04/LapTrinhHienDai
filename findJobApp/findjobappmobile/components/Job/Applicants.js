import { useEffect, useState } from "react";
import { View, Text, Linking, FlatList } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { Button, Card, Paragraph } from "react-native-paper";
import AsyncStorage from "@react-native-async-storage/async-storage";
import API, { authApis, endpoints } from "../../configs/API";
import moment from "moment";

const Applicants = ({ route }) => {
  const { jobId } = route.params;
  const [applications, setApplications] = useState([]);

const load = async () => {
  try {
    const token = await AsyncStorage.getItem("access_token");
    const url = endpoints["apply-job"](jobId);
    const res = await authApis(token).get(url);
    setApplications(res.data);
  } catch (err) {
    Alert.alert(" Lỗi load ứng viên:", err.response?.data || err.message);
  }
};

  useEffect(() => {
    load();
  }, []);

const updateStatus = async (id, status) => {
  try {
    const token = await AsyncStorage.getItem("access_token");
    const url = endpoints[status === "approved" ? "apply-approve" : "apply-reject"](id);
    const res = await authApis(token).patch(url);
    load(); 
  } catch (err) {
    Alert.alert("Lỗi", "Không thể cập nhật trạng thái. Vui lòng thử lại!");
  }
};

  return (
<SafeAreaView style={{ flex: 1 }}>
  <FlatList
    contentContainerStyle={{ padding: 10 }}
    data={applications}
    keyExtractor={item => item.id.toString()}
    renderItem={({ item }) => (
      <Card key={item.id} style={{ marginBottom: 10 }}>
        <Card.Title title={item.candidate?.username || "Người dùng"} />
        <Card.Content>
          <Text>📄 CV: {item.cv_link}</Text>
          <Text>⏰ {moment(item.applied_date).fromNow()}</Text>
          <Text>
            Trạng thái: {
              item.status === "approved" ? "✅ Chấp nhận" :
              item.status === "rejected" ? "❌ Từ chối" :
              "⏳ Đang chờ"
            }
          </Text>
        </Card.Content>
        <Card.Actions>
          {item.status === "pending" && (
            <View style={{ flexDirection: "row" }}>
              <Button onPress={() => updateStatus(item.id, "approved")}>✅ Duyệt</Button>
              <Button onPress={() => updateStatus(item.id, "rejected")}>❌ Từ chối</Button>
            </View>
          )}
          <Button onPress={() => Linking.openURL(item.cv_link)}>Xem CV</Button>
        </Card.Actions>
      </Card>
    )}
  />
</SafeAreaView>
  );
};

export default Applicants;