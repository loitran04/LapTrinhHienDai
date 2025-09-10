import AsyncStorage from "@react-native-async-storage/async-storage";
import { useNavigation, useRoute } from "@react-navigation/native";
import { useContext, useState } from "react"
import { Alert, KeyboardAvoidingView, Platform, View } from "react-native";
import { Icon } from "react-native-paper";
import { SafeAreaView } from "react-native-safe-area-context";
import MyInput, { MyButton, validateInput } from "./MyInput";
import API, { authApis, endpoints } from "../../configs/API";
import { MyDispatchContext } from "../../configs/Contexts";
import MyStyles from "../../styles/MyStyles";
import { CLIENT_ID, CLIENT_SECRET } from '@env';
import qs from 'qs';

const Login = () => {
  const [user, setUser] = useState({});
  const [error, setError] = useState({});
  const [enabled, setEnabled] = useState(true);
  const dispatch = useContext(MyDispatchContext);
  const nav = useNavigation();
  const fields = {
    'username': {
      'label': 'Tên đăng nhập', 'icon': 'account',
      'required': 'Vui lòng nhập tên đăng nhập!'
    }, 
    'password': {
      'label': 'Mật khẩu', 'icon': 'eye',
      'required': 'Vui lòng nhập mật khẩu!',
      'secure': true
    }
  };
  const validate = () => {
    return validateInput(user, setError, 'required', fields);
  };
  
const login = async () => {
  if (validate()) {
    try {
      setEnabled(false);
      const data = qs.stringify({
        username: user.username,
        password: user.password,
        grant_type: 'password',
        client_id: CLIENT_ID,  
        client_secret: CLIENT_SECRET,
      });
      let res = await API.post(endpoints['login'], data, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      });

      await AsyncStorage.setItem('access_token', res.data.access_token);

      let u = await authApis(res.data.access_token).get(endpoints['current_user']);
      dispatch({ type: 'login', payload: u.data });
      nav.navigate('Main', { screen: 'Trang chủ' });
    } catch (err) {
      console.log("Lỗi đăng nhập:", err.response?.data || err.message);
      Alert.alert('findJobApp', 'Tên đăng nhập hoặc mật khẩu không đúng!');
    } finally {
      setEnabled(true);
    }
  }
};
  return (
    <SafeAreaView style={MyStyles.container}>
    <KeyboardAvoidingView
      style={{flex: 1}}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}>
        <View style={MyStyles.aSelfCenter}>
          <Icon source="login-variant" size={200} color="#530065" />
        </View>
        {Object.keys(fields).map(k => (
          <MyInput key={k} field={k} setState={setUser}
            value={user[k]} error={error[k]} {...fields[k]} />
        ))}
      <View style={[MyStyles.row, MyStyles.flexEnd]}>
        <MyButton icon="account" onPress={login} label="Đăng nhập" enabled={enabled} />
      </View>
    </KeyboardAvoidingView>
    </SafeAreaView>
  )
}

export default Login;