import java.util.Arrays;
import java.time.LocalDate;
/**
 * This program display parameters passing.
 * 
 * @version 1.10 2021-11-09
 * @author He Yongqiang
 */
public class DataTest {
	
	
	public static void change(int a, int b)
	{
		int temp = b;
		b = a;
		a = temp;
	}
	public static void change1(Data a, Data b)
	{
		Data temp = b;
		b = a;
		a = temp;
	}
	public static void change2(Data a, Data b,int x,int y)
	{
		a.setValue(x);
		b.setValue(y);
	}
	
	public static void main(String[] args)
	{
		int x = 10;
		int y = 20;
		//形参的交换不影响实际参数的值
		change(x, y);
		System.out.println("x="+x);
		System.out.println("y="+y);
		///////////////////////////
		Data ix = new Data(100);
		Data iy = new Data(200);
		//形参的交换不影响实际参数的值
		change1(ix, iy);
		System.out.println(ix.getValue());
		System.out.println(iy.getValue());
		//////////////////////////////////
		//在change2中对形参指向的对象进行了修改
		change2(ix, iy,123,789);
		System.out.println(ix.getValue());
		System.out.println(iy.getValue());
		
	}

}

class Data
{
	private int value;
	public Data(int v)
	{value=v;}
	public int getValue()
	{
		return value;
	}
	public void setValue(int v)
	{
		value=v;
	}
}
