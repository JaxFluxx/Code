package innerClass;

import java.time.LocalDate;

import innerClass.Person.Body;
/**
 * 这是一个包含了内部类Body的类Person
 * @version 1.0 2018-12-9
 * @author He, yongqiang
 *
 */
public class Person
{
	private String name;
	private String gender;
	private LocalDate birthDate;	
	
	public Person() {};
	public Person(String name, String gender, LocalDate birthDate)
	{
		this.name=name;
		this.gender=gender;
		this.birthDate=birthDate;
	}
	public String getName()
	{
		return name;
	}
	public String getGender()
	{
		return gender;
	}
	public LocalDate getBirthDate()
	{
		return birthDate;
	}
	
	//定义一个非静态内部类
	public class Body
	{
		private double height;
		private double weight;

		public Body() {};
		public Body(double h, double w)
		{
			this.height=h;
			this.weight=w;
		}
		public double getHeight()
		{
			return height;
		}
		public double getWeight()
		{
			return weight;
		}
		public void setHeight(double h)
		{
			this.height=h;
		}
		public void setWeight(double w)
		{
			this.weight=w;
		}
		
		public void personInfo() //内部类可以访问外部类的任何成员
		{
			System.out.println("Name: " + name + "\nGender: " + gender);
		}
		@Override
		public String toString()
		{
			return "[The height is: "+height +"; The weight is: "+weight + "]";
		}
		
	}//内部类结束
	
	public String bodyInfo() 
	{
		//外部类通过内部类对象，可以访问内部类的任何成员
		Body body =new Body();
		body.setHeight(1.75);  //private
		body.setWeight(65.5);  //private
		body.height=1.8;       //private
		body.personInfo();     //public
		return body.toString();
	}
	public static void main(String[] args)
	{
		Person p1=new Person("John Key", "male",LocalDate.parse("1981-05-08"));
		System.out.println(p1.bodyInfo());
		Body body2=new Person("张文","男",LocalDate.parse("1976-05-12")).new Body(1.70,60);
		body2.personInfo();
		System.out.println("身高："+body2.getHeight());
		System.out.println("体重："+body2.getWeight());
//		Body body3 =new Body(1.78, 66.5);  //不能在static方法中使用非static内部类
	}
}
