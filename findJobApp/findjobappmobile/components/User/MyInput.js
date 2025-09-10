import * as ImgPicker from 'expo-image-picker';
import { Image, Text, View } from 'react-native';
import MyStyles from '../../styles/MyStyles';
import { useRef, useState } from 'react';
import { Button, HelperText, Icon, Menu, Portal, TextInput, TouchableRipple } from 'react-native-paper';
import { changeState } from '../../configs/Utils';

const MyInput = ({ setState, ...props}) => {
    if (props.type === 'select') return <MySelect {...props} setState={setState} />;
    const pickImage = async () => {
        let { status } = await ImgPicker.requestMediaLibraryPermissionsAsync();
        if (status === 'granted') {
            const r = await ImgPicker.launchImageLibraryAsync();
            if (!r.canceled) 
                changeState(setState, props.field, r.assets[0]);
        }
    }

    if (props.type === 'image')
        return <MyFileInput value={props.value} pickImage={pickImage}/>
    return <MyInputText {...props}
        onChangeText={t => changeState(setState, props.field, t)}/>
}
export default MyInput;
export const MyButton = ({ label, icon, onPress, enabled=true, mode= "contained", ...props}) => {
    return <Button style={MyStyles.mar} icon={icon} 
                    mode={mode} onPress={onPress} disable={!enabled}
                    loading={!enabled} {...props}>{label}</Button>
}

export const validateInput = (user, setError, type, ...args) => {
  let err = {};
  let ok = true;

  if (type === 'required') {
    const fields = args[0]; 
    for (let k of Object.keys(fields)) {
      if (fields[k].required && !user[k]) {
        err[k] = fields[k].required;
        ok = false;
      }
    }
  }

  if (type === 'match') {
    const [field1, field2, msg] = args;
    if (user[field1] !== user[field2]) {
      err[field1] = msg || 'Không khớp!';
      ok = false;
    }
  }

  setError(err);
  return ok;
};

const MyInputText = ({ icon, error, ...props }) => {
    const [secure, setSecure] = useState(props.secure || false);
    const iconPress = () => icon === 'eye' && setSecure(!secure) ;
    return (
        <>
        <TextInput {...props} style={MyStyles.mar} secureTextEntry={secure}
            right={<TextInput.Icon onPress={iconPress} icon={icon} 
            color={icon === 'eye' && !secure && "#530065"}/>}/>
        {!error||<HelperText type="error">{error}</HelperText>}
        </>
    );
}

const MyFileInput = ({ value, pickImage }) => {
    return (
        <>
        <TouchableRipple rippleColor="rgba(0, 0, 0, .32)" onPress={pickImage} 
                        style={[MyStyles.mar, MyStyles.pad]}>
            <Text>Chọn ảnh đại diện...</Text>
        </TouchableRipple>
        {value ? <Image source={{ uri: value.uri }} style={MyStyles.thumnail}/> : ""}
        </>
    );
}
const MySelect = ({ field, value, error, setState, options = [], label }) => {
  const [visible, setVisible] = useState(false);
  const selected = options.find(o => o.value === value);
  const selectedLabel = selected?.label || 'Chọn...';

  return (
    <View style={MyStyles.mar}>
      <Text style={{ marginBottom: 5, fontSize: 14 }}>{label}</Text>

      <Menu
        visible={visible}
        onDismiss={() => setVisible(false)}
        anchor={
          <TouchableRipple
            onPress={() => setVisible(true)}
            style={MyStyles.selectInput}
            >
            <View style={MyStyles.row}>
                <Icon source="account-tie" size={20} />
                <Text style={[MyStyles.info, { color: selected ? '#000' : '#999' }]}>
                {selectedLabel}
                </Text>
            </View>
          </TouchableRipple>
        }
      >
        {options.map(opt => (
          <Menu.Item
            key={opt.value}
            title={opt.label}
            onPress={() => {
              changeState(setState, field, opt.value);
              setVisible(false);
            }}
          />
        ))}
      </Menu>
      <HelperText type="error" visible={!!error}>
        {error}
      </HelperText>
    </View>
  );
};

