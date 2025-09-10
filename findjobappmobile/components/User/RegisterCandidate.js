import { useState } from "react";
import { changeState } from "../../configs/Utils";
import { KeyboardAvoidingView, Platform, View, ScrollView, Alert } from "react-native";
import MyStyles from "../../styles/MyStyles";
import { Icon } from "react-native-paper";
import MyInput, { MyButton, validateInput } from "./MyInput";
import { useNavigation } from '@react-navigation/native';
import API, { endpoints } from "../../configs/API";
import { SafeAreaView } from "react-native-safe-area-context";

export default Register = () => {
  const [user, setUser] = useState({});
  const [error, setError] = useState({});
  const [enabled, setEnabled] = useState(true);
  const nav = useNavigation();

  const fields = {
    'name': {
      'label': 'Họ và tên', 'icon': 'text',
      'required': 'Vui lòng nhập tên!'
    }, 'email': {
      'label': 'Email', 'icon': 'email',
      'required': 'Vui lòng nhập email!'
    }, 'username': {
      'label': 'Tên đăng nhập', 'icon': 'account',
      'required': 'Vui lòng nhập tên đăng nhập!'
    } , 'cv_link': {
        'label': 'Link CV', 'icon': 'link',
        'required': 'Vui lòng nhập link CV!',
        'type': 'url'
    }, 'password': {
      'label': 'Mật khẩu', 'icon': 'eye',
      'required': 'Vui lòng nhập mật khẩu!',
      'secure': true
    }, 'confirm_password': {
      'label': 'Xác nhận mật khẩu',
      'icon': 'eye',
      'required': "Vui lòng xác nhận mật khẩu!",
      'secure': true,
      'match': 'password',
    }, 'avatar': {
      'label': 'Ảnh đại diện', 'icon': 'image',
      'type': 'image',
    }
  };

  const validate = () => {
  const requiredOk = validateInput(user, setError, 'required', fields);
  const matched = validateInput(user, setError, 'match', 'confirm_password', 'password', "Mật khẩu không khớp!");
  const validCV = user.cv_link?.startsWith("http://") || user.cv_link?.startsWith("https://");
  if (!validCV) {
    setError(prev => ({ ...prev, cv_link: "CV phải là link hợp lệ!" }));
    return false;
  }

  return requiredOk && matched && validCV;
};

  const register = async () => {
  if (!validate()) {
    console.log("Validate thất bại", error);
    return;
  }

  const form = new FormData();
  for (let key of Object.keys(user)) {
    if (key !== 'confirm_password') {
      if (key === 'avatar' && user.avatar) {
        form.append('avatar', {
          uri: user.avatar.uri,
          type: user.avatar.mimeType || 'image/jpeg',
          name: user.avatar.fileName || 'avatar.jpg',
        });
      } else {
        form.append(key, user[key]);
      }
    }
  }

  try {
    setEnabled(false);
    const res = await API.post(endpoints['register-candidate'], form, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });

    if (res.status === 201) {
      Alert.alert('Đăng ký thành công', 'Bạn có thể đăng nhập ngay!');
      nav.navigate('Login');
    }
  } catch (ex) {
    console.log("Lỗi đăng ký:", ex.response?.data || ex.message);
    Alert.alert("Lỗi đăng ký", JSON.stringify(ex.response?.data || {}));
    setError({ ...error, ...ex.response?.data });
  } finally {
    setEnabled(true);
  }
};
  

  const reset = () => {
    Object.keys(user).forEach(k => changeState(setUser, k, ''));
  };

  return (
    <SafeAreaView style={MyStyles.container}>
    <KeyboardAvoidingView
      style={{flex: 1}}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}>
      <ScrollView>
        <View style={MyStyles.aSelfCenter}>
          <Icon source="account-circle" size={200} color="#530065" />
        </View>
        {Object.keys(fields).map(k => (
          <MyInput key={k} field={k} setState={setUser}
            value={user[k]} error={error[k]} {...fields[k]} />
        ))}
      </ScrollView>
      <View style={[MyStyles.row, MyStyles.flexEnd]}>
        <MyButton icon="refresh" onPress={reset} label="Nhập lại" />
        <MyButton icon="account" onPress={register} label="Đăng ký" enabled={enabled} />
      </View>
    </KeyboardAvoidingView>
    </SafeAreaView>
  );
};
