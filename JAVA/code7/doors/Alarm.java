package doors;
/**
 * This program displays a test for the interface operations .
 * @version 1.0 2018-11-25
 * @author He Yongqiang
 */
public interface Alarm
{
	void alarm() throws InterruptedException;  //默认为public abstract，不写方法体
	String INFORMATION = "这是一个报警接口的常量信息。";  //默认为public static final
	public static void info()   //static方法，接口名.方法名调用
	{
		System.out.println("正在调用Alarm接口的static方法。"); 
	}
	default void addInfo() //默认方法，即带方法体的实例方法，可以在实现时覆盖，也可以不覆盖
	{
		System.out.println("有人在开门，请查看！");
	}
}
