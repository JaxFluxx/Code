
/**
 * This program displays a test for the parameter passing.
 * @version 1.0 2018-09-10
 * @author He Yongqiang
 */
public class DataChangeTest{
	public static void main(String[] args)
	{
		DataChange dc = new DataChange(5);
		
		fun(dc, 10);
		dc.show();	
		
		DataChange dc1 = new DataChange(100);
		DataChange dc2 = new DataChange(200);
		swap(dc1,dc2);
		dc1.show();  //100
		dc2.show();	//200

	}
	public static void fun(DataChange datac,int ix)
	{
		datac.change(ix);		
	}
	public static void swap(DataChange dc1, DataChange dc2)
	{
		DataChange temp = dc1;
		dc1=dc2;
		dc2=temp;
//		dc2.change(10);
	} 
}
class DataChange 
{
	private int value;
	public DataChange(int a)
	{
		this.value = a;
	}
	public void change(int x)
	{
		value*=x;
	}
	public void show()
	{
		System.out.println("value="+ value);
	}
}