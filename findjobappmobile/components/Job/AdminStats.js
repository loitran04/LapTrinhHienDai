import { useEffect, useState } from "react";
import { SafeAreaView, Text, ScrollView, Dimensions } from "react-native";
import { BarChart } from "react-native-chart-kit";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { authApis, endpoints } from "../../configs/API";

const screenWidth = Dimensions.get("window").width;

const AdminStats = () => {
  const [labels, setLabels] = useState([]);
  const [data, setData] = useState({ jobs: [], candidates: [], employers: [] });

  const loadStats = async () => {
    try {
      const token = await AsyncStorage.getItem("access_token");
      const res = await authApis(token).get(endpoints["stats"]);
      const raw = res.data;
  
      const allMonths = [
        ...new Set([
          ...Object.keys(raw.jobs_created),
          ...Object.keys(raw.candidates_registered),
          ...Object.keys(raw.employers_registered),
        ])
      ];
  
      const sortedMonths = allMonths.sort((a, b) => new Date(a) - new Date(b));
      setLabels(sortedMonths);
  
      setData({
        jobs: sortedMonths.map(m => raw.jobs_created[m] || 0),
        candidates: sortedMonths.map(m => raw.candidates_registered[m] || 0),
        employers: sortedMonths.map(m => raw.employers_registered[m] || 0),
      });
    } catch (err) {
      console.error("Lỗi thống kê:", err.response?.data || err.message);
    }
  };

  useEffect(() => {
    loadStats();
  }, []);

  const chartConfig = {
    backgroundColor: "#fff",
    backgroundGradientFrom: "#fff",
    backgroundGradientTo: "#fff",
    decimalPlaces: 0,
    color: (opacity = 1) => `rgba(66, 66, 66, ${opacity})`,
    labelColor: () => "#333",
    barPercentage: 0.6,
    propsForBackgroundLines: {
      strokeDasharray: "",
      stroke: "#ccc"
    },
  };

  const renderChart = (label, dataset, color) => (
    <>
      <Text style={{ fontWeight: "bold", fontSize: 16, marginTop: 20, marginBottom: 10 }}>{label}</Text>
      <BarChart
        data={{
          labels: labels,
          datasets: [{ data: dataset }]
        }}
        width={screenWidth - 20}
        height={250}
        fromZero={true}
        yAxisLabel=""
        chartConfig={{
          ...chartConfig,
          color: () => color,
        }}
        verticalLabelRotation={30}
        style={{
          borderRadius: 12,
          padding: 10,
          marginBottom: 16
        }}
      />
    </>
  );

  return (
    <SafeAreaView style={{ flex: 1, padding: 10, backgroundColor: "#f5f5f5" }}>
      <ScrollView>
        {renderChart("📊 Số việc làm theo tháng", data.jobs, "#3366cc")}
        {renderChart("👤 Số ứng viên đăng ký", data.candidates, "#dc3912")}
        {renderChart("🏢 Số nhà tuyển dụng đăng ký", data.employers, "#ff9900")}
      </ScrollView>
    </SafeAreaView>
  );
};

export default AdminStats;
