import { useEffect, useState } from "react";
import { View, Text, ScrollView, Image, Alert } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { Card, Button} from "react-native-paper";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { authApis, endpoints } from "../../configs/API";

const AdminVerification = () => {
  const [employers, setEmployers] = useState([]);

  const loadEmployers = async () => {
    try {
      const token = await AsyncStorage.getItem("access_token");
      const res = await authApis(token).get(endpoints["employers"]);
      const unverified = res.data.filter(e => !e.verified);
      setEmployers(unverified);
    } catch (err) {
      Alert.alert("Lỗi", "Không thể tải danh sách nhà tuyển dụng.");
    }
  };

  const approve = async (id) => {
    try {
      const token = await AsyncStorage.getItem("access_token");
      await authApis(token).patch(endpoints["employer-details"](id), {
        verified: true
      });
      Alert.alert("Đã xác minh thành công!");
      loadEmployers();
    } catch (err) {
      Alert.alert("Lỗi", "Không thể xác minh.");
    }
  };

  const reject = async (id) => {
    Alert.alert("Xác nhận", "Bạn có chắc muốn xoá nhà tuyển dụng này?", [
      {
        text: "Huỷ", style: "cancel"
      },
      {
        text: "Xoá", style: "destructive", onPress: async () => {
          try {
            const token = await AsyncStorage.getItem("access_token");
            await authApis(token).delete(endpoints["employer-details"](id));
            Alert.alert("Đã xoá nhà tuyển dụng.");
            loadEmployers();
          } catch (err) {
            Alert.alert("Lỗi", "Không thể xoá.");
          }
        }
      }
    ]);
  };

  useEffect(() => {
    loadEmployers();
  }, []);

  return (
    <SafeAreaView style={{ flex: 1, padding: 12 }}>
      <ScrollView>
        {employers.map((e) => (
          <Card key={e.id} style={{ marginBottom: 16, padding: 10 }}>
            <Text variant="titleLarge">🏢 {e.name}</Text>
            <Text>📄 Tax code: {e.tax_code}</Text>
            <Text>📍 Location: {e.location}</Text>

            <Text style={{ fontWeight: "bold", marginTop: 8, marginBottom: 4 }}>
              Ảnh môi trường:
            </Text>
            <ScrollView horizontal showsHorizontalScrollIndicator={false}>
              {(e.images || []).map((img, idx) => (
                <Image
                  key={idx}
                  source={{ uri: img.image || img }}
                  style={{ width: 100, height: 100, marginRight: 8, borderRadius: 8 }}
                />
              ))}
            </ScrollView>

            <View style={{ flexDirection: "row", justifyContent: "space-between", marginTop: 12 }}>
              <Button mode="contained" onPress={() => approve(e.id)}>Duyệt xác minh</Button>
              <Button mode="outlined" textColor="red" onPress={() => reject(e.id)}>Từ chối</Button>
            </View>
          </Card>
        ))}
        {employers.length === 0 && (
          <Text style={{ textAlign: "center", marginTop: 40 }}>
            Không có nhà tuyển dụng nào cần xác minh.
          </Text>
        )}
      </ScrollView>
    </SafeAreaView>
  );
};

export default AdminVerification;
