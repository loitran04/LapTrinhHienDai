import { StyleSheet } from 'react-native';
export default StyleSheet.create({
  container: {
    flex: 1,
    padding: 8,
    backgroundColor: '#fff',
  },
  row: {
    flexDirection: "row",
    flexWrap: "wrap",
    justifyContent: "space-evenly",
    alignItems: "center",
  },
  flexStart: {
    justifyContent: "flex-start",
  },
  flexEnd: {
    justifyContent: "flex-end",
  },
  aSelfCenter: {
    alignSelf: "center",
  }, thumnail: {
    width: 100,
    height: 100,
    borderRadius: 20,
  },
  avatar: {
    width: 50,
    height: 50,
    borderRadius: 50,
  },
  subject: {
    fontSize: 20,
    fontWeight: "bold",
  },
  info: {
    marginTop: 5,
    marginRight: 5,
  },
  pad: {
    padding: 5,
  },
  mar: {
    margin: 5,
  },
  helpText: {
    color: 'darkred',
    fontSize: 16,
    fontStyle: 'italic',
  },
  textarea: {
    height: 100,
  }, selectInput: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    borderWidth: 1,
    borderRadius: 6,
    paddingVertical: 12,
    paddingHorizontal: 12,
    backgroundColor: '#f7f2fa',
    borderColor: '#ccc',
  }, wrapper: {
    flex: 1,
    justifyContent: 'space-between',
  },
  scroll: {
    padding: 16,
    paddingBottom: 32, 
  },
  card: {
    backgroundColor: '#f2f2f2',
    borderRadius: 10,
    padding: 12,
    marginBottom: 12,
  },
  footer: {
    paddingHorizontal: 16,
    paddingBottom: 16,
    paddingTop: 8,
    backgroundColor: '#fff',
    borderTopWidth: 1,
    borderColor: '#eee',
  }, profile: {
    width: 200, height: 200, borderRadius: 200
    }, name: {
    fontSize: 40, margin: 10, fontWeight: "bold"
    }, profileWrapper: {
    padding: 24,
    alignItems: "center",
    flex: 1,
    backgroundColor: "#fff",
  },
  avatar: {
    width: 160,
    height: 160,
    borderRadius: 80,
    borderWidth: 3,
    borderColor: "#7e22ce",
    marginBottom: 10,
  },
  fullName: {
    fontSize: 20,
    fontWeight: "600",
    color: "#000",
    marginBottom: 10,
  },
  logoutBtn: {
    marginBottom: 20,
    borderColor: "#7e22ce",
    borderWidth: 1,
  },
  infoRow: {
    flexDirection: "row",
    marginBottom: 12,
    width: "100%",
    alignItems: "center",
  },
  infoLabel: {
    fontSize: 16,
    fontWeight: "500",
    width: 100,
    color: "#555",
  },
  infoValue: {
    fontSize: 16,
    color: "#222",
    flex: 1,
  },
});