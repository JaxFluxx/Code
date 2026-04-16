package lambda;

import java.util.Arrays;
import java.util.Comparator;
/**
 * 该程序实现一个Dog数组的排序，演示了各种代码块重用的实现方法：
 * 1.两个函数的嵌套调用
 * 2.类中实现接口，以实现类的对象做函数参数传递代码块
 * 3.以匿名类做函数参数传递代码块，这时不需要实现接口
 * 4.以lambda表达式做函数参数 传递代码块， 这时不需要实现接口
 * @version 1.1 2021-12-5
 * @author He, Yongqiang 
 *
 */
public class ArraysSort
{

	public static void printDogs(Dog[] dogs)
	{
		System.out.println("--Dog List--");
		for (Dog d : dogs)
			System.out.println(d);

	}
	
	//定义一个比较大小的方法，该方法将用于排序方法的调用
	public static int aCompare(int w1, int w2)
	{
		return w1-w2;
	}
	
	//定义一个对数组排序的方法，该方法中调用了比较方法
	public static void aSort(Dog[] dA)  
	{
		for(int i=0;i<dA.length-1;i++)
			for(int j=0; j<dA.length-1-i;j++)
			{
				if(aCompare(dA[j+1].getWeight(),dA[j].getWeight())<0)
				{
					Dog temp=dA[j];
					dA[j]=dA[j+1];
					dA[j+1]=temp;
				}
			}
	}
	
	public static void main(String[] args)
	{
		Dog d1 = new Dog("Max", "black", 50);
		Dog d2 = new Dog("Rocky", "yellow", 35);
		Dog d3 = new Dog("Bear", "brown", 45);
		Dog d4 = new Dog("Lucky", "white", 40);

		Dog[] dogArray = { d1, d2, d3, d4 };
		printDogs(dogArray);
		
// 第一种方法：在一个方法中调用另一个方法
		aSort(dogArray);		
		
// 第二种方法：Dog类中实现了Comparator接口，则可以用Dog类对象作为sort的第二个参数：
//		Arrays.sort(dogArray, new Dog());
		
		
// 第三种方法：Dog类中不再实现Comparator接口，而以一个匿名类作为sort方法的第二个参数：		
		/*Arrays.sort(dogArray, new Comparator<Dog>() 
		{
			@Override
			public int compare(Dog dog1, Dog dog2)
			{
				return dog1.getWeight()-dog2.getWeight();
			}
		});*/		
		
		
// 第四种方法：Dog类中不再实现Comparator接口，而以一个lambda表达式作为sort方法的第二个参数：		
//		Arrays.sort(dogArray, (dog1, dog2) -> dog1.getWeight() - dog2.getWeight());
//按名字排序的lambda表达式：		
//		Arrays.sort(dogArray, (dog1, dog2) -> dog1.getName().compareTo(dog2.getName()));


		printDogs(dogArray);
	}
}