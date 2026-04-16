package arrayList;

import java.util.ArrayList;
/**
 * 这个类演示了包装类型在ArraList中的使用，以及数组参数的传递.
 * @version 1.10 2021-11-28
 * @author He Yongqiang
 */
public class PrimitiveArrayList
{
	public static void main(String[] args) 
	{
		var list = new ArrayList<Integer>();
		for(int i=0;i<10;++i)
			list.add(i+1);  //自动装箱，相当于：list.add(Integer.valueOf(i+1))
		for(Integer value:list)
			System.out.println(value);
		Integer a=100;
		Integer b=100;
		System.out.println(a==b);
		System.out.println(a.equals(b));
		
		//包装器是不可变类	
				
		int[] aInt =new int[] {1,2,3,4,5};
		
		for(int i=0;i<aInt.length;++i)
			changeInt(aInt[i],10);  //由于值传递，通过函数不能改变元素的值
		for(int value:aInt)
			System.out.println(value);
			
		changeIntArray(aInt,10);  //传递的参数是数组，方法中通过这个引用值改变数组的元素值。
		for(int value:aInt)   
			System.out.println(value);
		
		
		Integer[] aInteger =new Integer[] {1,2,3,4,5};
		for(int i=0;i<aInteger.length;++i)
			changeInteger(aInteger[i],100);  //由于值传递，通过函数不能改变元素的值
		for(int value:aInteger)
			System.out.println(value);
		
		
		changeIntegerArray(aInteger,100);
		for(int value:aInteger)
			System.out.println(value);
		
	}
	
	public static void changeInt(int n,int x)
	{		
			n*=x;			
	}
	public static void changeInteger(Integer n,int x)
	{		
			n*=x;			
	}
	
	public static void changeIntArray(int[] n,int x)
	{
		for(int i=0;i<n.length;++i)
			n[i]*=x;
			
	}
	public static void changeIntegerArray(Integer[] n,int x)
	{
		for(int i=0;i<n.length;++i)
			n[i]*=x;
			
	}
	
		
}
