import { useNavigation } from "@react-navigation/native";
import { useContext, useEffect, useState } from "react";
import { MyDispatchContext, MyUserContext } from "../../configs/Contexts";
import { Image, Text, View } from "react-native";
import { Button, Divider } from "react-native-paper";
import moment from "moment";
import "moment/locale/vi";
import MyStyles from "../../styles/MyStyles";
import API, { authApis, endpoints } from "../../configs/API";
import AsyncStorage from '@react-native-async-storage/async-storage';
import { SafeAreaView } from "react-native-safe-area-context";

const Profile = () => {
  const user = useContext(MyUserContext);
  const dispatch = useContext(MyDispatchContext);
  const nav = useNavigation();
  const [fullName, setFullName] = useState("...");

  const logout = async () => {
  await AsyncStorage.removeItem("access_token");
  dispatch({ type: "logout" });
  nav.navigate("Login");
};

  const loadProfileName = async () => {
    try {
      const token = await AsyncStorage.getItem('access_token');
      if (!token) throw new Error("Không có token");
      let url = "";
      if (user.role === "candidate")
        url = endpoints["current-candidate"];
      else if (user.role === "employer")
        url = endpoints["current-employer"];

      const res = await authApis(token).get(url);
      setFullName(res.data.name || "(Admin)");
    } catch (err) {
      console.error("Lỗi load tên người dùng:", err.response?.data || err.message);
    }
  };

  useEffect(() => {
    loadProfileName();
  }, []);

  return (
    <SafeAreaView style={MyStyles.container}>
      <View style={MyStyles.profileWrapper}>
        <Image source={{ uri: user.avatar }} style={MyStyles.avatar} />
        <Text style={MyStyles.fullName}>{fullName}</Text>

        <Button
          icon="logout"
          mode="outlined"
          style={MyStyles.logoutBtn}
          onPress={logout}
          textColor="#7e22ce"
        >
          Đăng xuất
        </Button>

        <Divider style={{ width: "100%", marginBottom: 20 }} />

        <Info label="Tài khoản" value={user.username} />
        <Info label="Email" value={user.email} />
        <Info label="Tham gia" value={moment(user.date_joined).fromNow()} />
      </View>
    </SafeAreaView>
  );
};

const Info = ({ label, value }) => (
  <View style={MyStyles.infoRow}>
    <Text style={MyStyles.infoLabel}>{label}</Text>
    <Text style={MyStyles.infoValue}>{value}</Text>
  </View>
);

export default Profile;
