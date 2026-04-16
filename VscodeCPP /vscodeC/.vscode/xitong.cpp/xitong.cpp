#include <iostream>
#include <string>
#include <vector>
#include <fstream>

using namespace std;

// 声明学生和管理员类
class Student;
class Admin;

// 空教室预约系统类
class ClassroomReservationSystem {
private:
    vector<Student> students; // 存储所有学生信息
    vector<Admin> admins; // 存储所有管理员信息
    string currentUserId; // 当前登录的用户ID
    string currentUserType; // 当前登录的用户类型

    // 加载学生和管理员信息
    void loadUsers() {
        ifstream studentFile("students.txt");
        ifstream adminFile("admins.txt");

        string line;
        while (getline(studentFile, line)) {
            string id, name, password;
            id = line;
            getline(studentFile, name);
            getline(studentFile, password);
            students.push_back(Student(id, name, password));
        }

        while (getline(adminFile, line)) {
            string id, name, password;
            id = line;
            getline(adminFile, name);
            getline(adminFile, password);
            admins.push_back(Admin(id, name, password));
        }

        studentFile.close();
        adminFile.close();
    }

    // 保存学生和管理员信息
    void saveUsers() {
        ofstream studentFile("students.txt");
        ofstream adminFile("admins.txt");

        for (const auto& student : students) {
            studentFile << student.getId() << endl;
            studentFile << student.getName() << endl;
            studentFile << student.getPassword() << endl;
        }

        for (const auto& admin : admins) {
            adminFile << admin.getId() << endl;
            adminFile << admin.getName() << endl;
            adminFile << admin.getPassword() << endl;
        }

        studentFile.close();
        adminFile.close();
    }

    // 显示主菜单
    void showMainMenu() {
        cout << "空教室预约系统" << endl;
        cout << "1. 学生登录" << endl;
        cout << "2. 管理员登录" << endl;
        cout << "3. 退出" << endl;
    }

    // 处理学生登录
    void handleStudentLogin() {
        cout << "请输入学生ID: ";
        string id;
        cin >> id;
        cout << "请输入密码: ";
        string password;
        cin >> password;

        for (auto& student : students) {
            if (student.getId() == id && student.getPassword() == password) {
                currentUserId = student.getId();
                currentUserType = "student";
                cout << "登录成功！" << endl;
                return;
            }
        }

        cout << "学生ID或密码错误！请重新登录。" << endl;
    }

    // 处理管理员登录
    void handleAdminLogin() {
        cout << "请输入管理员ID: ";
        string id;
        cin >> id;
        cout << "请输入密码: ";
        string password;
        cin >> password;

        for (auto& admin : admins) {
            if (admin.getId() == id && admin.getPassword() == password) {
                currentUserId = admin.getId();
                currentUserType = "admin";
                cout << "登录成功！" << endl;
                return;
            }
        }

        cout << "管理员ID或密码错误！请重新登录。" << endl;
    }

    // 处理学生操作
    void handleStudentOptions() {
        int choice;
        while (true) {
            cout << "学生操作菜单" << endl;
            cout << "1. 预约空教室" << endl;
            cout << "2. 取消已预约的教室" << endl;
            cout << "3. 查看已预约的教室" << endl;
            cout << "4. 返回上一级菜单" << endl;
            cout << "请选择操作: ";
            cin >> choice;

            switch (choice) {
                case 1:
                    // 预约空教室
                    reserveClassroom();
                    break;
                case 2:
                    // 取消已预约的教室
                    cancelReservation();
                    break;
                case 3:
                    // 查看已预约的教室
                    viewReservedClassrooms();
                    break;
                case 4:
                    // 返回上一级菜单
                    return;
                default:
                    cout << "无效的选择！请重新选择。" << endl;
                    break;
            }
        }
    }

    // 处理管理员操作
    void handleAdminOptions() {
        int choice;
        while (true) {
            cout << "管理员操作菜单" << endl;
            cout << "1. 添加学生" << endl;
            cout << "2. 删除学生" << endl;
            cout << "3. 添加管理员" << endl;
            cout << "4. 删除管理员" << endl;
            cout << "5. 返回上一级菜单" << endl;
            cout << "请选择操作: ";
            cin >> choice;

            switch (choice) {
                case 1:
                    // 添加学生
                    addStudent();
                    break;
                case 2:
                    // 删除学生
                    deleteStudent();
                    break;
                case 3:
                    // 添加管理员
                    addAdmin();
                    break;
                case 4:
                    // 删除管理员
                    deleteAdmin();
                    break;
                case 5:
                    // 返回上一级菜单
                    return;
                default:
                    cout << "无效的选择！请重新选择。" << endl;
                    break;
            }
        }
    }

    // 预约空教室
    void reserveClassroom() {
        string classroom;
        cout << "请输入要预约的教室: ";
        cin >> classroom;

        // 在此添加预约教室的逻辑
        // ...

        cout << "教室预约成功！" << endl;
    }

    // 取消已预约的教室
    void cancelReservation() {
        string classroom;
        cout << "请输入要取消预约的教室: ";
        cin >> classroom;

        // 在此添加取消预约教室的逻辑
        // ...

        cout << "教室预约已取消！" << endl;
    }

    // 查看已预约的教室
    void viewReservedClassrooms() {
        // 在此添加查看已预约教室的逻辑
        // ...
    }

    // 添加学生
    void addStudent() {
        string id, name, password;
        cout << "请输入学生ID: ";
        cin >> id;
        cout << "请输入学生姓名: ";
        cin >> name;
        cout << "请输入密码: ";
        cin >> password;

        students.push_back(Student(id, name, password));
        saveUsers();

        cout << "学生添加成功！" << endl;
    }

    // 删除学生
    void deleteStudent() {
        string id;
        cout << "请输入要删除的学生ID: ";
        cin >> id;

        for (auto it = students.begin(); it != students.end(); ++it) {
            if (it->getId() == id) {
                students.erase(it);
                saveUsers();
                cout << "学生删除成功！" << endl;
                return;
            }
        }

        cout << "找不到要删除的学生ID！" << endl;
    }

    // 添加管理员
    void addAdmin() {
        string id, name, password;
        cout << "请输入管理员ID: ";
        cin >> id;
        cout << "请输入管理员姓名: ";
        cin >> name;
        cout << "请输入密码: ";
        cin >> password;

        admins.push_back(Admin(id, name, password));
        saveUsers();

        cout << "管理员添加成功！" << endl;
    }

    // 删除管理员
    void deleteAdmin() {
        string id;
        cout << "请输入要删除的管理员ID: ";
        cin >> id;

        for (auto it = admins.begin(); it != admins.end(); ++it) {
            if (it->getId() == id) {
                admins.erase(it);
                saveUsers();
                cout << "管理员删除成功！" << endl;
                return;
            }
        }

        cout << "找不到要删除的管理员ID！" << endl;
    }

public:
    ClassroomReservationSystem() {
        loadUsers();
    }

    // 运行空教室预约系统
    void run() {
        int choice;
        while (true) {
            showMainMenu();
            cout << "请选择操作: ";
            cin >> choice;
            cin.ignore(); // 忽略输入缓冲

            switch (choice) {
                case 1:
                    // 学生登录
                    handleStudentLogin();
                    if (currentUserType == "student") {
                        handleStudentOptions();
                    }
                    break;
                case 2:
                    // 管理员登录
                    handleAdminLogin();
                    if (currentUserType == "admin") {
                        handleAdminOptions();
                    }
                    break;
                case 3:
                    // 退出
                    saveUsers();
                    return;
                default:
                    cout << "无效的选择！请重新选择。" << endl;
                    break;
            }
        }
    }
};

// 学生类
class Student {
private:
    string id;
    string name;
    string password;

public:
    Student(string id, string name, string password) {
        this->id = id;
        this->name = name;
        this->password = password;
    }

    string getId() const {
        return id;
    }

    string getName() const {
        return name;
    }

    string getPassword() const {
        return password;
    }
};

// 管理员类
class Admin {
private:
    string id;
    string name;
    string password;

public:
    Admin(string id, string name, string password) {
        this->id = id;
        this->name = name;
        this->password = password;
    }

    string getId() const {
        return id;
    }

    string getName() const {
        return name;
    }

    string getPassword() const {
        return password;
    }
};

int main() {
    ClassroomReservationSystem system;
    system.run();
    return 0;
}
