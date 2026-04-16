
class First {
	public  double PI = 3.1415926;
	public  void info() {
		System.out.println("Value of First is " + PI);
	}
}
class Second extends First {
	public static double E = 2.71828;
//	public static void info() {
//		System.out.println("Value of Second is " + E);
//	}
}
public class Statictest {
	public static void main(String[] args) {
		Second second =new Second();
		second.info();
		System.out.println(Second.E);
		System.out.println(second.PI);
	}
}