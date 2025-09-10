import { TouchableOpacity, Text, View } from 'react-native';
import MyStyles from '../../styles/MyStyles';
import he from 'he';

const Item = ({ instance, onPress }) => {
  return (
    <TouchableOpacity
      onPress={onPress}
      style={[MyStyles.pad, MyStyles.mar, { backgroundColor: '#f2f2f2', borderRadius: 10, elevation: 1 }]}
    >
      <Text style={MyStyles.subject}>{instance.title}</Text>
      <Text style={MyStyles.info}>📍 {instance.location}</Text>
      <Text style={MyStyles.info}>💰 {instance.salary} đ</Text>
      <Text style={MyStyles.info}>🕒 {instance.work_hours} giờ</Text>
      <Text numberOfLines={2} style={[MyStyles.info, { fontStyle: 'italic', color: '#666' }]}>
  {he.decode(instance.description.replace(/<[^>]*>/g, ''))}
</Text>
    </TouchableOpacity>
  );
};

export default Item;
