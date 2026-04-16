package doors;
/**
 * This program displays a test for the interface operations .
 * @version 1.1 2021-11-25
 * @author He Yongqiang
 */
public class UsingDoor
{

	public static void main(String[] args) throws InterruptedException
	{
		AlarmDoor myDoor = new AlarmDoor(210,150,"Blue",1);
		myDoor.open();
		myDoor.close();
		
		System.out.println(Alarm.INFORMATION);  //使用接口中的常量
		Alarm.info();                  //调用接口中的static方法

	}

}
